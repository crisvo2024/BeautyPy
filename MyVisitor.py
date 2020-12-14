import sys
import os
import sublime
if not ((os.path.dirname(__file__) + '/gen') in sys.path):
    sys.path.append((os.path.dirname(__file__) + '/gen'))
from Python3Parser import Python3Parser
from Python3Visitor import Python3Visitor
import re
from itertools import chain, cycle


class MyVisitor(Python3Visitor):
    view = None

    def __init__(self, arr):
        self.view = arr[0]
        self.edit = arr[1]
        self.offset_col = 0
        self.offset_row = 0
        self.current_row = -1
        self.opened = []

    def veryfi_line_chage(self, child):
        if child.getSymbol().line + self.offset_row == self.current_row[-1]:
            return False
        return True

    def insert_in_row(self, new, row, col: int = 0):
        if row != self.current_row:
            self.offset_col = 0
            self.current_row = row
        self.view.insert(self.edit, self.view.text_point(row + self.offset_row, col + self.offset_col), new)
        self.offset_col += len(new)
        if len(new.splitlines()) > 1:
            self.offset_row += len(new.splitlines())-1

    def replace_in_row(self, obj, new, row):
        if row != self.current_row:
            self.offset_col = 0
            self.current_row = row
        allcontent = sublime.Region(0, self.view.size())
        lines = self.view.substr(allcontent).splitlines()
        for index, line in enumerate(lines):
            symbols = re.findall(obj, line)
            if symbols:
                lines[index] = line.replace(
                    obj,
                    new)
        self.view.replace(self.edit, allcontent, '\n'.join(lines))
        self.offset_col += len(new) - len(obj)
        if len(new.splitlines()) > 1:
            self.offset_row += len(new.splitlines())-1

    def add_blank_line(self, row, col):
        self.insert_in_row('\n', row, col)
        self.offset_row += 1

    def is_empty_chain(self, lista):
        ac = 0
        for i in lista:
            if i == ' ' or i == '\n':
                ac += 1
        if ac == len(lista):
            return True
        else:
            return False

    def exist_blank_line(self, child, where, symbol):
        lin = child.getSymbol().line + self.offset_row
        #print("linea", lin)
        col = int(child.getSymbol().column)
        point = self.view.text_point(lin-1,col+1)
        line = self.view.substr(self.view.full_line(point))
        res = list(line)
        if where == 'after':
            for index, l in enumerate(res):
                if index != len(res)-1 and l[index] == '\n':
                    return True
        elif where == 'before':
            point = self.view.text_point(lin-1, col+1)
            line = self.view.substr(self.view.full_line(point))
            res = list(line)
            ac = res.count(symbol)
            if ac == 1:
                subLine = res[0:res.index(symbol)+1]
                if self.is_empty_chain(subLine):
                    print("es cadena vacia")
                    return False
                else:
                    return True
            # elif ac > 1:
                # for j in range(ac):


    def erase_in_place(self, row, col1, col2):
        point1 = self.view.text_point(row + self.offset_row, col1 + self.offset_col)
        point2 = self.view.text_point(row + self.offset_row, col2 + self.offset_col)
        self.view.erase(self.edit, sublime.Region(point1, point2))

    def eliminate_whitespaces(self, child, where):
        lin = child.getSymbol().line
        if self.current_row != lin:
            self.offset_col = 0
        self.current_row = lin
        lin += self.offset_row
        col = int(child.getSymbol().column) + self.offset_col
        point = self.view.text_point(lin-1, col+1)
        line = self.view.substr(self.view.line(point))
        res = list(line)
        if where == 'after':
            try:
                while res[col+1] == ' ' or res[col+1] == '\t':
                    res.pop(col+1)
                    if res[col+1] == '\t':
                        tab = self.view.find('\t', point)
                        self.offset_col -= tab.end() - tab.begin()
                    else:
                        self.offset_col -= 1
            except IndexError:
                pass
        elif where == 'before':
            try:
                while res[col-1] == ' ' or res[col-1] == '\t':
                    res.pop(col-1)
                    if res[col-1] == '\t':
                        tab = self.view.find('\t', point)
                        self.offset_col -= tab.end() - tab.begin()
                    else:
                        self.offset_col -= 1
                    col -= 1
            except IndexError:
                pass
        line = ''.join(res)
        self.view.replace(self.edit, self.view.line(point), line)

    def add_whitespace_after(self, child):
        lin = child.getSymbol().line
        if self.current_row != lin:
            self.offset_col = 0
        self.current_row = lin
        self.eliminate_whitespaces(child, 'before')
        lin += self.offset_row
        col = int(child.getSymbol().column) + self.offset_col
        self.eliminate_whitespaces(child, 'after')
        point = self.view.text_point(lin-1, col+1)
        line = self.view.substr(self.view.line(point))
        res = list(line)
        try:
            res.insert(col+1, ' ')
            self.offset_col += 1
        except IndexError:
            pass
        line = ''.join(res)
        self.view.replace(self.edit, self.view.line(point), line)

    # Tiene que tener las comas despues de las comas revisar cuando se haga E231:
    def organize_imports(self, child):
        lin = child.getSymbol().line
        if self.current_row != lin:
            self.offset_col = 0
        self.current_row = lin
        self.eliminate_whitespaces(child, 'before')
        lin += self.offset_row
        col = int(child.getSymbol().column) + self.offset_col
        self.eliminate_whitespaces(child, 'after')
        # self.add_whitespace_after(child)
        point = self.view.text_point(lin-1, col+1)
        line = self.view.substr(self.view.line(point))
        res = list(line)
        try:
            res.insert(col+1, ' ')
            self.offset_col += 1
        except IndexError:
            pass
        self.offset_col -= (len(line[6:col+1]))  # 6 -> len('import')
        res[col] = '\nimport'
        self.offset_row += 1
        line = ''.join(res)
        self.view.replace(self.edit, self.view.line(point), line)

    def whitespace_around(self, child):
        spaces = len(child.getText())
        lin = child.getSymbol().line
        if self.current_row != lin:
            self.offset_col = 0
        self.current_row = lin
        lin += self.offset_row
        self.eliminate_whitespaces(child,'before')
        col = int(child.getSymbol().column) + self.offset_col
        point = self.view.text_point(lin-1, col+1)
        line = self.view.substr(self.view.line(point))
        res = list(line)
        try:
            while res[col+spaces] == ' ' or res[col+spaces] == '\t':
                res.pop(col+spaces)
                if res[col+spaces] == '\t':
                    tab = self.view.find('\t', point)
                    self.offset_col -= tab.end() - tab.begin()
                else:
                    self.offset_col -= 1
        except IndexError:
            pass
        res.insert(col, ' ')
        res.insert(col+spaces+1, ' ')
        self.offset_col += 2
        line = ''.join(res)
        self.view.replace(self.edit, self.view.line(point), line)

    # Visit a parse tree produced by Python3Parser#single_input.
    def visitSingle_input(self, ctx: Python3Parser.Single_inputContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#file_input.
    def visitFile_input(self, ctx: Python3Parser.File_inputContext):
        # self.view.insert(self.edit, 0, "Hello, World!")
        # print(ctx.getText(),sys.stdout)
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#eval_input.
    def visitEval_input(self, ctx: Python3Parser.Eval_inputContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#decorator.
    def visitDecorator(self, ctx: Python3Parser.DecoratorContext):
        # E201, E202, E211:
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#decorators.
    def visitDecorators(self, ctx: Python3Parser.DecoratorsContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#decorated.
    def visitDecorated(self, ctx: Python3Parser.DecoratedContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#async_funcdef.
    def visitAsync_funcdef(self, ctx: Python3Parser.Async_funcdefContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#funcdef.
    def visitFuncdef(self, ctx: Python3Parser.FuncdefContext):
        # E203:
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#parameters.
    def visitParameters(self, ctx: Python3Parser.ParametersContext):
        # E201, E202, E211:
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#typedargslist.
    def visitTypedargslist(self, ctx: Python3Parser.TypedargslistContext):
        # TERMINAR E231 -->
        # if ctx.getChild(0).getText() == '*':
        #     if ctx.getChild(1).getText() == ',':
        # elif ctx.getChild(0).getText() == '**':
        #
        # else:
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#tfpdef.
    def visitTfpdef(self, ctx: Python3Parser.TfpdefContext):
        # E203:
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#varargslist.
    def visitVarargslist(self, ctx: Python3Parser.VarargslistContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#vfpdef.
    def visitVfpdef(self, ctx: Python3Parser.VfpdefContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#stmt.
    def visitStmt(self, ctx: Python3Parser.StmtContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#simple_stmt.
    def visitSimple_stmt(self, ctx: Python3Parser.Simple_stmtContext):
        if ctx.small_stmt(1):
            j = 1
            for i in ctx.small_stmt():
                self.visitSmall_stmt(i)
                if ctx.getChild(j).getText() == ';':
                    self.add_whitespace_after(ctx.getChild(j))
                j += 2
        else:
            self.visitSmall_stmt(ctx.small_stmt(0))
            if ctx.getChild(1) and ctx.getChild(1).getText() == ';':
                self.add_whitespace_after(ctx.getChild(1))
        return

    # Visit a parse tree produced by Python3Parser#small_stmt.
    def visitSmall_stmt(self, ctx: Python3Parser.Small_stmtContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#expr_stmt.
    def visitExpr_stmt(self, ctx: Python3Parser.Expr_stmtContext):
        if ctx.ASSIGN():
            self.visitTestlist_star_expr(ctx.testlist_star_expr(0))
            j = 2
            for i in ctx.ASSIGN():
                self.whitespace_around(i)
                if 'yield' in ctx.getChild(j).getText():
                    self.visitYield_expr(ctx.getChild(j))
                else:
                    self.visitTestlist_star_expr(ctx.getChild(j))
                j += 2
        else:
            self.visitChildren(ctx)
        return

    # Visit a parse tree produced by Python3Parser#annassign.
    def visitAnnassign(self, ctx: Python3Parser.AnnassignContext):
        # E203:
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#testlist_star_expr.
    def visitTestlist_star_expr(self, ctx: Python3Parser.Testlist_star_exprContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#augassign.
    def visitAugassign(self, ctx: Python3Parser.AugassignContext):
        self.whitespace_around(ctx.getChild(0))
        return

    # Visit a parse tree produced by Python3Parser#del_stmt.
    def visitDel_stmt(self, ctx: Python3Parser.Del_stmtContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#pass_stmt.
    def visitPass_stmt(self, ctx: Python3Parser.Pass_stmtContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#flow_stmt.
    def visitFlow_stmt(self, ctx: Python3Parser.Flow_stmtContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#break_stmt.
    def visitBreak_stmt(self, ctx: Python3Parser.Break_stmtContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#continue_stmt.
    def visitContinue_stmt(self, ctx: Python3Parser.Continue_stmtContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#return_stmt.
    def visitReturn_stmt(self, ctx: Python3Parser.Return_stmtContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#yield_stmt.
    def visitYield_stmt(self, ctx: Python3Parser.Yield_stmtContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#raise_stmt.
    def visitRaise_stmt(self, ctx: Python3Parser.Raise_stmtContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#import_stmt.
    def visitImport_stmt(self, ctx: Python3Parser.Import_stmtContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#import_name.
    def visitImport_name(self, ctx: Python3Parser.Import_nameContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#import_from.
    def visitImport_from(self, ctx: Python3Parser.Import_fromContext):
        # E201, E202, E211:
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#import_as_name.
    def visitImport_as_name(self, ctx: Python3Parser.Import_as_nameContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#dotted_as_name.
    def visitDotted_as_name(self, ctx: Python3Parser.Dotted_as_nameContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#import_as_names.
    def visitImport_as_names(self, ctx: Python3Parser.Import_as_namesContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#dotted_as_names.
    def visitDotted_as_names(self, ctx: Python3Parser.Dotted_as_namesContext):
        # E401:
        # Arreglar cuando se mezcla con la regla E231!!!!
        # for i in ctx.comma():
        #     self.visitComma(i)
        j = 1
        for i in ctx.dotted_as_name():
            self.visitDotted_as_name(i)
            if ctx.getChild(j):
                # self.add_whitespace_after(ctx.getChild(j).getChild(0))
                self.organize_imports(ctx.getChild(j).getChild(0))
            j += 2
        return

    # Visit a parse tree produced by Python3Parser#dotted_name.
    def visitDotted_name(self, ctx: Python3Parser.Dotted_nameContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#global_stmt.
    def visitGlobal_stmt(self, ctx: Python3Parser.Global_stmtContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#nonlocal_stmt.
    def visitNonlocal_stmt(self, ctx: Python3Parser.Nonlocal_stmtContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#assert_stmt.
    def visitAssert_stmt(self, ctx: Python3Parser.Assert_stmtContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#compound_stmt.
    def visitCompound_stmt(self, ctx: Python3Parser.Compound_stmtContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#async_stmt.
    def visitAsync_stmt(self, ctx: Python3Parser.Async_stmtContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#if_stmt.
    def visitIf_stmt(self, ctx: Python3Parser.If_stmtContext):
        # E203:
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#while_stmt.
    def visitWhile_stmt(self, ctx: Python3Parser.While_stmtContext):
        # E203:
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#for_stmt.
    def visitFor_stmt(self, ctx: Python3Parser.For_stmtContext):
        # E203:
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#try_stmt.
    def visitTry_stmt(self, ctx: Python3Parser.Try_stmtContext):
        # E203:
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#with_stmt.
    def visitWith_stmt(self, ctx: Python3Parser.With_stmtContext):
        # E203:
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#with_item.
    def visitWith_item(self, ctx: Python3Parser.With_itemContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#except_clause.
    def visitExcept_clause(self, ctx: Python3Parser.Except_clauseContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#suite.
    def visitSuite(self, ctx: Python3Parser.SuiteContext):
        # print(ctx.INDENT().getText()+'f')
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#test.
    def visitTest(self, ctx: Python3Parser.TestContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#test_nocond.
    def visitTest_nocond(self, ctx: Python3Parser.Test_nocondContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#lambdef.
    def visitLambdef(self, ctx: Python3Parser.LambdefContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#lambdef_nocond.
    def visitLambdef_nocond(self, ctx: Python3Parser.Lambdef_nocondContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#or_test.
    def visitOr_test(self, ctx: Python3Parser.Or_testContext):
        j = 1
        for i in ctx.and_test():
            self.visitAnd_test(i)
            if ctx.getChild(j):
                self.whitespace_around(ctx.getChild(j))
            j += 2
        return

    # Visit a parse tree produced by Python3Parser#and_test.
    def visitAnd_test(self, ctx: Python3Parser.And_testContext):
        j = 1
        for i in ctx.not_test():
            self.visitNot_test(i)
            if ctx.getChild(j):
                self.whitespace_around(ctx.getChild(j))
            j += 2
        return

    # Visit a parse tree produced by Python3Parser#not_test.
    def visitNot_test(self, ctx: Python3Parser.Not_testContext):
        if ctx.getChild(0).getText() == 'not':
            self.whitespace_around(ctx.getChild(0))
            self.visitNot_test(ctx.not_test())
        else:
            self.visitComparison(ctx.comparison())
        return

    # Visit a parse tree produced by Python3Parser#comparison.
    def visitComparison(self, ctx: Python3Parser.ComparisonContext):
        i = 1
        for j in ctx.expr():
            self.visitExpr(j)
            if ctx.getChild(i):
                lin = ctx.getChild(i).getChild(0).getSymbol().line + self.offset_row
                # print("linea", lin)
                col = int(ctx.getChild(i).getChild(0).getSymbol().column)
                if ctx.getChild(i).getText() == '!=' and (ctx.getChild(i+1).getText() == 'True' or ctx.getChild(i+1).getText() == 'False' or ctx.getChild(i+1).getText() == 'None'):
                    self.replace_in_row('!=', 'is not ', lin-1)
                elif ctx.getChild(i).getText() == '==' and (ctx.getChild(i+1).getText() == 'True' or ctx.getChild(i+1).getText() == 'False' or ctx.getChild(i+1).getText() == 'None'):
                    self.replace_in_row('==', 'is ', lin-1)
            i += 2
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#comp_op.
    def visitComp_op(self, ctx: Python3Parser.Comp_opContext):
        self.whitespace_around(ctx.getChild(0))
        if ctx.getChild(1):
            self.whitespace_around(ctx.getChild(1))
        return

    # Visit a parse tree produced by Python3Parser#star_expr.
    def visitStar_expr(self, ctx: Python3Parser.Star_exprContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#expr.
    def visitExpr(self, ctx: Python3Parser.ExprContext):
        j = 1
        for i in ctx.xor_expr():
            self.visitXor_expr(i)
            if ctx.getChild(j):
                self.whitespace_around(ctx.getChild(j))
            j += 2
        return
        # if ctx.getChild(1):
        #     initial_line = ctx.getChild(1).getSymbol().line + self.offsef_row
        #     column = int(ctx.getChild(1).getSymbol().column+1)
        #     print(ctx.getChild(1))
        #     if not self.exist_blank_line(ctx.getChild(1), 'before', '|'):
        #         print("entro")
        #         self.add_blank_line(initial_line -1, column)
        # return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#xor_expr.
    def visitXor_expr(self, ctx: Python3Parser.Xor_exprContext):
        j = 1
        for i in ctx.and_expr():
            self.visitAnd_expr(i)
            if ctx.getChild(j):
                self.whitespace_around(ctx.getChild(j))
            j += 2
        return

    # Visit a parse tree produced by Python3Parser#and_expr.
    def visitAnd_expr(self, ctx: Python3Parser.And_exprContext):
        j = 1
        for i in ctx.shift_expr():
            self.visitShift_expr(i)
            if ctx.getChild(j):
                self.whitespace_around(ctx.getChild(j))
            j += 2
        return

    # Visit a parse tree produced by Python3Parser#shift_expr.
    def visitShift_expr(self, ctx: Python3Parser.Shift_exprContext):
        j = 1
        for i in ctx.arith_expr():
            self.visitArith_expr(i)
            if ctx.getChild(j):
                self.whitespace_around(ctx.getChild(j))
            j += 2
        return

    # Visit a parse tree produced by Python3Parser#arith_expr.
    def visitArith_expr(self, ctx: Python3Parser.Arith_exprContext):
        j = 1
        for i in ctx.term():
            self.visitTerm(i)
            if ctx.getChild(j):
                self.whitespace_around(ctx.getChild(j))
            j += 2
        return

    # Visit a parse tree produced by Python3Parser#term.
    def visitTerm(self, ctx: Python3Parser.TermContext):
        j = 1
        for i in ctx.factor():
            self.visitFactor(i)
            if ctx.getChild(j):
                self.whitespace_around(ctx.getChild(j))
            j += 2
        return

    # Visit a parse tree produced by Python3Parser#factor.
    def visitFactor(self, ctx: Python3Parser.FactorContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#power.
    def visitPower(self, ctx: Python3Parser.PowerContext):
        self.visitAtom_expr(ctx.atom_expr())
        if ctx.factor():
            self.whitespace_around(ctx.getChild(1))
            self.visitFactor(ctx.factor())
        return

    # Visit a parse tree produced by Python3Parser#atom_expr.
    def visitAtom_expr(self, ctx: Python3Parser.Atom_exprContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#atom.
    def visitAtom(self, ctx: Python3Parser.AtomContext):
        if ctx.OPEN_BRACE() or ctx.OPEN_BRACK():
            lin = ctx.getChild(0).getSymbol().line
            if self.current_row != lin:
                self.offset_col = 0
            self.current_row = lin
            open_line = ctx.getChild(0).getSymbol().line + self.offset_row - 1
            open_column = ctx.getChild(0).getSymbol().column + self.offset_col
            self.eliminate_whitespaces(ctx.getChild(0), 'after')
            self.visitChildren(ctx)
            self.eliminate_whitespaces(list(ctx.getChildren())[-1], 'before')
            if open_line - (list(ctx.getChildren())[-1].getSymbol().line + self.offset_row - 1) == 0:
                return
            lines = (list(ctx.getChildren())[-1].getSymbol().line + self.offset_row - 1) - open_line - 1
            if self.view.substr(self.view.text_point(open_line, open_column + 1)) == '\n':
                suite = ctx.parentCtx
                try:
                    while not isinstance(suite, Python3Parser.SuiteContext):
                        suite = suite.parentCtx
                except AttributeError:
                    suite = SuiteCtx()
                if self.view.substr(self.view.line(self.view.text_point(open_line + 1 + lines, 0))) not in [']', '}']:
                    lines += 1
                    anterior = self.view.substr(self.view.line(self.view.text_point(open_line + 1 + lines, 0)))
                    self.offset_col += 4 - len(re.findall(r'\s*', anterior)[0])
                for i in range(lines):
                    anterior = self.view.substr(self.view.line(self.view.text_point(open_line + 1 + i, 0)))
                    nueva = re.sub(r'^\s*', suite.INDENT().getText() + "    ", anterior)
                    self.view.replace(self.edit, self.view.line(self.view.text_point(open_line + 1 + i, 0)), nueva)
                self.insert_in_row(suite.INDENT().getText(), list(ctx.getChildren())[-1].getSymbol().line - 1, 0)
                return
            spaces = ' ' * (open_column + 1)
            for i in range(lines):
                anterior = self.view.substr(self.view.line(self.view.text_point(open_line + 1 + i, 0)))
                nueva = re.sub(r'^\s*', spaces, anterior)
                self.view.replace(self.edit, self.view.line(self.view.text_point(open_line + 1 + i, 0)), nueva)
            if self.view.substr(self.view.text_point(open_line + 1 + lines, 0)) in ['}', ']']:
                spaces = ' ' * (open_column
                                - (list(ctx.getChildren())[-1].getSymbol().column + self.offset_col - 1))
                self.insert_in_row(spaces, list(ctx.getChildren())[-1].getSymbol().line - 1, 0)
            else:
                anterior = self.view.substr(self.view.line(self.view.text_point(open_line + 1 + lines, 0)))
                self.offset_col -= len(re.findall(r'\s*', anterior)[0])
                nueva = re.sub(r'^\s*', spaces, anterior)
                self.view.replace(self.edit, self.view.line(self.view.text_point(open_line + 1 + lines, 0)), nueva)
            self.offset_col += len(spaces)
        else:
            self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#testlist_comp.
    def visitTestlist_comp(self, ctx: Python3Parser.Testlist_compContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#trailer.
    def visitTrailer(self, ctx: Python3Parser.TrailerContext):
        if ctx.OPEN_BRACK():
            self.eliminate_whitespaces(ctx.OPEN_BRACK(), 'before')
            open_line = ctx.OPEN_BRACK().getSymbol().line + self.offset_row - 1
            open_column = ctx.OPEN_BRACK().getSymbol().column + self.offset_col
            self.eliminate_whitespaces(ctx.OPEN_BRACK(), 'after')
            self.visitSubscriptlist(ctx.subscriptlist())
            self.eliminate_whitespaces(ctx.CLOSE_BRACK(), 'before')
            if open_line - (ctx.CLOSE_BRACK().getSymbol().line + self.offset_row - 1) == 0:
                return
            lines = (ctx.CLOSE_BRACK().getSymbol().line + self.offset_row - 1) - open_line - 1
            if self.view.substr(self.view.text_point(open_line, open_column + 1)) == '\n':
                suite = ctx.parentCtx
                try:
                    while not isinstance(suite, Python3Parser.SuiteContext):
                        suite = suite.parentCtx
                except AttributeError:
                    suite = SuiteCtx()
                if self.view.substr(self.view.line(self.view.text_point(open_line + 1 + lines, 0))) != ']':
                    lines += 1
                    anterior = self.view.substr(self.view.line(self.view.text_point(open_line + 1 + lines, 0)))
                    self.offset_col += 4 - len(re.findall(r'\s*', anterior)[0])
                for i in range(lines):
                    anterior = self.view.substr(self.view.line(self.view.text_point(open_line + 1 + i, 0)))
                    nueva = re.sub(r'^\s*', suite.INDENT().getText() + "    ", anterior)
                    self.view.replace(self.edit, self.view.line(self.view.text_point(open_line + 1 + i, 0)), nueva)
                self.insert_in_row(suite.INDENT().getText(), ctx.CLOSE_BRACK().getSymbol().line - 1, 0)
                return
            spaces = ' ' * (open_column + 1)
            for i in range(lines):
                anterior = self.view.substr(self.view.line(self.view.text_point(open_line + 1 + i, 0)))
                nueva = re.sub(r'^\s*', spaces, anterior)
                self.view.replace(self.edit, self.view.line(self.view.text_point(open_line + 1 + i, 0)), nueva)
            if self.view.substr(self.view.text_point(open_line + 1 + lines, 0)) == ']':
                spaces = ' ' * (open_column
                                - (ctx.CLOSE_BRACK().getSymbol().column + self.offset_col - 1))
                self.insert_in_row(spaces, ctx.CLOSE_BRACK().getSymbol().line - 1, 0)
            else:
                anterior = self.view.substr(self.view.line(self.view.text_point(open_line + 1 + lines, 0)))
                self.offset_col -= len(re.findall(r'\s*', anterior)[0])
                nueva = re.sub(r'^\s*', spaces, anterior)
                self.view.replace(self.edit, self.view.line(self.view.text_point(open_line + 1 + lines, 0)), nueva)
            self.offset_col += len(spaces)
        else:
            self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#subscriptlist.
    def visitSubscriptlist(self, ctx: Python3Parser.SubscriptlistContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#subscript.
    def visitSubscript(self, ctx: Python3Parser.SubscriptContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#sliceop.
    def visitSliceop(self, ctx: Python3Parser.SliceopContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#exprlist.
    def visitExprlist(self, ctx: Python3Parser.ExprlistContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#testlist.
    def visitTestlist(self, ctx: Python3Parser.TestlistContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#dictorsetmaker.
    def visitDictorsetmaker(self, ctx: Python3Parser.DictorsetmakerContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#classdef.
    def visitClassdef(self, ctx: Python3Parser.ClassdefContext):
        # E201, E202:
        # self.insert_in_row("\nHello World\n", final_line+1)
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#arglist.
    def visitArglist(self, ctx: Python3Parser.ArglistContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#argument.
    def visitArgument(self, ctx: Python3Parser.ArgumentContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#comp_iter.
    def visitComp_iter(self, ctx: Python3Parser.Comp_iterContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#comp_for.
    def visitComp_for(self, ctx: Python3Parser.Comp_forContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#comp_if.
    def visitComp_if(self, ctx: Python3Parser.Comp_ifContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#encoding_decl.
    def visitEncoding_decl(self, ctx: Python3Parser.Encoding_declContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#yield_expr.
    def visitYield_expr(self, ctx: Python3Parser.Yield_exprContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#yield_arg.
    def visitYield_arg(self, ctx: Python3Parser.Yield_argContext):
        return self.visitChildren(ctx)

        # Visit a parse tree produced by Python3Parser#open_paren.
    def visitOpen_paren(self, ctx: Python3Parser.Open_parenContext):
        self.eliminate_whitespaces(ctx.getChild(0), 'before')
        self.eliminate_whitespaces(ctx.getChild(0), 'after')
        self.opened.append(
            [ctx.getChild(0).getSymbol().column + self.offset_col, ctx.getChild(0).getSymbol().line + self.offset_row - 1])
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#close_paren.
    def visitClose_paren(self, ctx: Python3Parser.Close_parenContext):
        self.eliminate_whitespaces(ctx.getChild(0), 'before')
        open_column = self.opened.pop()
        if ctx.getChild(0).getSymbol().line - 1 == open_column[1]:
            return
        lines = (ctx.getChild(0).getSymbol().line + self.offset_row - 1) - open_column[1] - 1
        if self.view.substr(self.view.text_point(open_column[1], open_column[0] + 1)) == '\n':
            suite = ctx.parentCtx
            try:
                while not isinstance(suite, Python3Parser.SuiteContext):
                    suite = suite.parentCtx
            except AttributeError:
                suite = SuiteCtx()
            if self.view.substr(self.view.line(self.view.text_point(open_column[1] + 1 + lines, 0))) != ')':
                lines += 1
                anterior = self.view.substr(self.view.line(self.view.text_point(open_column[1] + 1 + lines, 0)))
                self.offset_col += 4 - len(re.findall(r'\s*', anterior)[0])
            for i in range(lines):
                anterior = self.view.substr(self.view.line(self.view.text_point(open_column[1] + 1 + i, 0)))
                nueva = re.sub(r'^\s*', suite.INDENT().getText() + "    ", anterior)
                self.view.replace(self.edit, self.view.line(self.view.text_point(open_column[1] + 1 + i, 0)), nueva)
            if self.view.substr(self.view.line(self.view.text_point(open_column[1] + 1 + lines, 0))) == ')':
                self.insert_in_row(suite.INDENT().getText(), ctx.getChild(0).getSymbol().line - 1, 0)
            return
        spaces = ' ' * (open_column[0] + 1)
        for i in range(lines):
            anterior = self.view.substr(self.view.line(self.view.text_point(open_column[1] + 1 + i, 0)))
            nueva = re.sub(r'^\s*', spaces, anterior)
            self.view.replace(self.edit, self.view.line(self.view.text_point(open_column[1] + 1 + i, 0)), nueva)
        if self.view.substr(self.view.text_point(open_column[1] + 1 + lines, 0)) == ']':
            spaces = ' ' * (open_column[0]
                            - (ctx.CLOSE_BRACK().getSymbol().column + self.offset_col - 1))
            self.insert_in_row(spaces, ctx.CLOSE_BRACK().getSymbol().line - 1, 0)
        else:
            anterior = self.view.substr(self.view.line(self.view.text_point(open_column[1] + 1 + lines, 0)))
            self.offset_col -= len(re.findall(r'\s*', anterior)[0])
            nueva = re.sub(r'^\s*', spaces, anterior)
            self.view.replace(self.edit, self.view.line(self.view.text_point(open_column[1] + 1 + lines, 0)), nueva)
        self.offset_col += len(spaces)

    # Visit a parse tree produced by Python3Parser#comma.
    def visitComma(self, ctx: Python3Parser.CommaContext):
        self.add_whitespace_after(ctx.getChild(0))
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#colon.
    def visitColon(self, ctx:Python3Parser.ColonContext):
        self.eliminate_whitespaces(ctx.getChild(0), 'before')
        return self.visitChildren(ctx)


class SuiteCtx:
    def INDENT(self):
        return self

    def getText(self):
        return ""