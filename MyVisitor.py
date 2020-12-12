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
        # self.current_row = list()
        # self.affected_cols = list()

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
            self.offset_row += len(new.splitlines()) - 1

    def erase_in_place(self, row, col1, col2):
        point1 = self.view.text_point(row + self.offsef, col1)
        point2 = self.view.text_point(row + self.offsef, col2)
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
        # print(res)
        # print(col)
        # print(lin)
        # print(child.getText())
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
                while res[col-1] == ' ':
                    res.pop(col-1)
                    self.offset_col -= 1
                    col -= 1
            except IndexError:
                pass
        line = ''.join(res)
        self.view.replace(self.edit, self.view.line(point), line)

    # #Prueba1:
    # def eliminate_whitespaces(self, child, where):
    #     lin = child.getSymbol().line
    #     if self.current_row != lin:
    #         self.offsef_col = 0
    #     self.current_row = lin
    #     lin += self.offsef_row
    #     col = int(child.getSymbol().column) + self.offsef_col
    #     point = self.view.text_point(lin-1, col+1)
    #     line = self.view.substr(self.view.line(point))
    #     wspaces = re.sub(r'\s\s\s\t', r'    ', line)
    #     wspaces = re.sub(r'\s\s\t', r'    ', wspaces)
    #     wspaces = re.sub(r'\s\t', r'    ', wspaces)
    #     wspaces = re.sub(r'\t', r'    ', wspaces)
    #     res = list(wspaces)
    #     # print(col)
    #     # print(lin)
    #     # print(child.getText())
    #     if where == 'after':
    #         while res[col+1] == ' ':
    #             res.pop(col+1)
    #             self.offsef_col -= 1
    #     elif where == 'before':
    #         while res[col-1] == ' ':
    #             self.offsef_col -= 1
    #             res.pop(col-1)
    #             col -= 1
    #     # print(res)
    #     line = ''.join(res)
    #     self.view.replace(self.edit, self.view.line(point), line)

    # Tiene que tener las comas despues de las comas revisar cuando se haga E231:
    def organize_imports(self, child):
        lin = child.getSymbol().line
        if self.current_row != lin:
            self.offset_col = 0
        self.current_row = lin
        lin += self.offset_row
        col = int(child.getSymbol().column) + self.offset_col
        point = self.view.text_point(lin-1, col+1)
        line = self.view.substr(self.view.line(point))
        res = list(line)
        # print(res)
        # print(col)
        # print(lin)
        # print(res[7:col + 1])
        # print("-------------------")
        self.offset_col -= (len(line[6:col + 1]))  # 6 -> len('import')
        res[col] = '\nimport'
        self.offset_row += 1
        line = ''.join(res)
        # print(line)
        self.view.replace(self.edit, self.view.line(point), line)

    # def whitespace_around(self, child):
    #     assign = False
    #     if len(child.getText()) == 2:
    #         assign = True
    #     lin = child.getSymbol().line
    #     if self.current_row != lin:
    #         self.offsef_col = 0
    #     self.current_row = lin
    #     lin += self.offsef_row
    #     self.eliminate_whitespaces(child,'before')
    #     col = int(child.getSymbol().column) + self.offsef_col
    #     print(col)
    #     self.eliminate_whitespaces(child,'after')
    #     point = self.view.text_point(lin-1, col+1)
    #     line = self.view.substr(self.view.line(point))
    #     res = line
    #     self.offsef_col += 2
    #     line = ''.join(res)
    #     # print(line)
    #     self.view.replace(self.edit, self.view.line(point), line)

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
        self.visitDotted_name(ctx.dotted_name())
        if ctx.getChild(2).getText() == '(':
            self.eliminate_whitespaces(ctx.getChild(2).getChild(0), 'before')
            self.eliminate_whitespaces(ctx.getChild(2).getChild(0), 'after')
            self.visitOpen_paren(ctx.open_paren())
            i = 3
            if ctx.arglist():
                self.visitArglist(ctx.arglist())
                i = 4
            self.eliminate_whitespaces(ctx.getChild(i).getChild(0), 'before')
            self.visitClose_paren(ctx.close_paren())
        return

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
        self.visitParameters(ctx.parameters())
        i = 3
        if ctx.test():
            self.visitTest(ctx.test())
            i = 5
        self.eliminate_whitespaces(ctx.getChild(i), 'before')
        self.visitSuite(ctx.suite())
        return

    # Visit a parse tree produced by Python3Parser#parameters.
    def visitParameters(self, ctx: Python3Parser.ParametersContext):
        # E201, E202, E211:
        self.eliminate_whitespaces(ctx.getChild(0).getChild(0), 'before')
        self.eliminate_whitespaces(ctx.getChild(0).getChild(0), 'after')
        self.visitOpen_paren(ctx.open_paren())
        i = 1
        if ctx.typedargslist:
            self.visitTypedargslist(ctx.typedargslist())
            i = 2
        self.eliminate_whitespaces(ctx.getChild(i).getChild(0), 'before')
        self.visitClose_paren(ctx.close_paren())
        return

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
        if ctx.test():
            self.eliminate_whitespaces(ctx.getChild(1), 'before')
            self.visitTest(ctx.test())
        return

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
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#small_stmt.
    def visitSmall_stmt(self, ctx: Python3Parser.Small_stmtContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#expr_stmt.
    def visitExpr_stmt(self, ctx: Python3Parser.Expr_stmtContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#annassign.
    def visitAnnassign(self, ctx: Python3Parser.AnnassignContext):
        # E203:
        self.eliminate_whitespaces(ctx.getChild(0), 'before')
        self.visitTest(ctx.test(0))
        if ctx.test(1):
            self.visitTest(ctx.test(1))
        return

    # Visit a parse tree produced by Python3Parser#testlist_star_expr.
    def visitTestlist_star_expr(self, ctx: Python3Parser.Testlist_star_exprContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#augassign.
    def visitAugassign(self, ctx: Python3Parser.AugassignContext):
        # self.whitespace_around(ctx.getChild(0))
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
        if ctx.dotted_name():
            self.visitDotted_name(ctx.dotted_name())
        i = 0
        while ctx.getChild(i).getText() != 'import':
            i += 1
        if ctx.getChild(i+1).getText() == '(':
            self.eliminate_whitespaces(ctx.getChild(i+1).getChild(0), 'before')
            self.eliminate_whitespaces(ctx.getChild(i+1).getChild(0), 'after')
            self.visitOpen_paren(ctx.open_paren())
            self.visitImport_as_names(ctx.import_as_names())
            self.eliminate_whitespaces(ctx.getChild(i+3).getChild(0), 'before')
            self.visitClose_paren(ctx.close_paren())
        elif ctx.getChild(i+1).getText() != '*':
            self.visitImport_as_names(ctx.import_as_names())
        return

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
        dotted = ctx.dotted_as_name()
        j = 1
        for i in dotted:
            self.visitDotted_as_name(i)
            if ctx.getChild(j):
                self.organize_imports(ctx.getChild(j))
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
        test = ctx.test()
        suite = ctx.suite()
        last_else = False
        if (len(test) + len(suite)) % 2 != 0:
            last_else = True
        j = 2
        for i in range(len(test)):
            self.visitTest(test[i])
            self.eliminate_whitespaces(ctx.getChild(j), 'before')
            self.visitSuite(suite[i])
            j += 4
        if last_else:
            self.eliminate_whitespaces(ctx.getChild(j-1), 'before')
            self.visitSuite(suite[-1])
        return

    # Visit a parse tree produced by Python3Parser#while_stmt.
    def visitWhile_stmt(self, ctx: Python3Parser.While_stmtContext):
        # E203:
        self.visitTest(ctx.test())
        self.eliminate_whitespaces(ctx.getChild(2), 'before')
        self.visitSuite(ctx.suite(0))
        if ctx.suite(1):
            self.eliminate_whitespaces(ctx.getChild(5), 'before')
            self.visitSuite(ctx.suite(1))
        return

    # Visit a parse tree produced by Python3Parser#for_stmt.
    def visitFor_stmt(self, ctx: Python3Parser.For_stmtContext):
        # E203:
        self.visitExprlist(ctx.exprlist())
        self.visitTestlist(ctx.testlist())
        self.eliminate_whitespaces(ctx.getChild(4), 'before')
        self.visitSuite(ctx.suite(0))
        if ctx.suite(1):
            self.eliminate_whitespaces(ctx.getChild(7), 'before')
            self.visitSuite(ctx.suite(1))
        return

    # Visit a parse tree produced by Python3Parser#try_stmt.
    def visitTry_stmt(self, ctx: Python3Parser.Try_stmtContext):
        # E203:
        self.eliminate_whitespaces(ctx.getChild(1), 'before')
        self.visitSuite(ctx.suite(0))
        if ctx.except_clause():
            exc = ctx.except_clause()
            j = 4
            for i in range(len(exc)):
                self.visitExcept_clause(ctx.except_clause(i))
                self.eliminate_whitespaces(ctx.getChild(j), 'before')
                self.visitSuite(ctx.suite(i+1))
                j += 3
            if ctx.suite(i+2):
                self.eliminate_whitespaces(ctx.getChild(j), 'before')
                self.visitSuite(ctx.suite(i+2))
            if ctx.suite(i+3):
                self.eliminate_whitespaces(ctx.getChild(j+3), 'before')
                self.visitSuite(ctx.suite(i+3))
        else:
            self.eliminate_whitespaces(ctx.getChild(4), 'before')
            self.visitSuite(ctx.suite(1))
        return

    # Visit a parse tree produced by Python3Parser#with_stmt.
    def visitWith_stmt(self, ctx: Python3Parser.With_stmtContext):
        # E203:
        withItem = ctx.with_item()
        for i in withItem:
            self.visitWith_item(i)
        self.eliminate_whitespaces(ctx.getChild(ctx.getChildCount()-2), 'before')
        self.visitSuite(ctx.suite())
        return

    # Visit a parse tree produced by Python3Parser#with_item.
    def visitWith_item(self, ctx: Python3Parser.With_itemContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#except_clause.
    def visitExcept_clause(self, ctx: Python3Parser.Except_clauseContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#suite.
    def visitSuite(self, ctx: Python3Parser.SuiteContext):
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
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#and_test.
    def visitAnd_test(self, ctx: Python3Parser.And_testContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#not_test.
    def visitNot_test(self, ctx: Python3Parser.Not_testContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#comparison.
    def visitComparison(self, ctx: Python3Parser.ComparisonContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#comp_op.
    def visitComp_op(self, ctx: Python3Parser.Comp_opContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#star_expr.
    def visitStar_expr(self, ctx: Python3Parser.Star_exprContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#expr.
    def visitExpr(self, ctx: Python3Parser.ExprContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#xor_expr.
    def visitXor_expr(self, ctx: Python3Parser.Xor_exprContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#and_expr.
    def visitAnd_expr(self, ctx: Python3Parser.And_exprContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#shift_expr.
    def visitShift_expr(self, ctx: Python3Parser.Shift_exprContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#arith_expr.
    def visitArith_expr(self, ctx: Python3Parser.Arith_exprContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#term.
    def visitTerm(self, ctx: Python3Parser.TermContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#factor.
    def visitFactor(self, ctx: Python3Parser.FactorContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#power.
    def visitPower(self, ctx: Python3Parser.PowerContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#atom_expr.
    def visitAtom_expr(self, ctx: Python3Parser.Atom_exprContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#atom.
    def visitAtom(self, ctx: Python3Parser.AtomContext):
        # E201, E202, E211:
        if ctx.getChild(0).getText() == '(':
            self.eliminate_whitespaces(ctx.getChild(0).getChild(0), 'before')
            self.eliminate_whitespaces(ctx.getChild(0).getChild(0), 'after')
            self.visitOpen_paren(ctx.open_paren())
            i = 1
            if ctx.yield_expr():
                self.visitYield_expr(ctx.yield_expr())
                i = 2
            elif ctx.testlist_comp():
                self.visitTestlist_comp(ctx.testlist_comp())
                i = 2
            self.eliminate_whitespaces(ctx.getChild(i).getChild(0), 'before')
            self.visitClose_paren(ctx.close_paren())
        elif ctx.getChild(0).getText() == '[':
            if ctx.testlist_comp():
                self.visitTestlist_comp(ctx.testlist_comp)
        elif ctx.getChild(0).getText() == '{':
            if ctx.dictorsetmaker():
                self.visitDictorsetmaker(ctx.dictorsetmaker())
        return

    # Visit a parse tree produced by Python3Parser#testlist_comp.
    def visitTestlist_comp(self, ctx: Python3Parser.Testlist_compContext):
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#trailer.
    def visitTrailer(self, ctx: Python3Parser.TrailerContext):
        # E201, E202:
        if ctx.getChild(0).getText() == '(':
            self.eliminate_whitespaces(ctx.getChild(0).getChild(0), 'before')
            self.eliminate_whitespaces(ctx.getChild(0).getChild(0), 'after')
            self.visitOpen_paren(ctx.open_paren())
            i = 1
            if ctx.arglist():
                self.visitArglist(ctx.arglist())
                i = 2
            self.eliminate_whitespaces(ctx.getChild(i).getChild(0), 'before')
            self.visitClose_paren(ctx.close_paren())
        elif ctx.getChild(0).getText() == '[':
            self.visitSubscriptlist(ctx.subscriptlist())
        return

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
        if ctx.getChild(2).getText() == '(':
            self.eliminate_whitespaces(ctx.getChild(2).getChild(0), 'before')
            self.eliminate_whitespaces(ctx.getChild(2).getChild(0), 'after')
            self.visitOpen_paren(ctx.open_paren())
            j = 3
            i = 4
            if ctx.arglist():
                self.visitArglist(ctx.arglist())
                j = 4
                i = 5
            self.eliminate_whitespaces(ctx.getChild(j).getChild(0), 'before')
            self.visitClose_paren(ctx.close_paren())
        else:
            i = 2
        self.eliminate_whitespaces(ctx.getChild(i), 'before')
        self.visitSuite(ctx.suite())
        # self.insert_in_row("\nHello World\n", final_line+1)

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
        self.opened.append([ctx.getChild(0).getSymbol().column, ctx.getChild(0).getSymbol().line])
        return self.visitChildren(ctx)

    # Visit a parse tree produced by Python3Parser#close_paren.
    def visitClose_paren(self, ctx: Python3Parser.Close_parenContext):
        close_column = self.opened.pop()
        print(close_column, sys.stdout)
        if ctx.getChild(0).getSymbol().line == close_column[1] \
                or self.view.substr(
                    self.view.text_point(close_column[1], close_column[0] + 1)
                ) == '\n':
            return
        if close_column[0] - ctx.getChild(0).getSymbol().column > 0:
            spaces = ''.join([' ' for _ in range(close_column[0] - ctx.getChild(0).getSymbol().column + 1)])
            self.insert_in_row(spaces, ctx.getChild(0).getSymbol().line-1, ctx.getChild(0).getSymbol().column)
        # elif close_column[0] - ctx.getChild(0).getSymbol().column < 0:
        #     self.erase_in_place(ctx.getChild(0).getSymbol().line, ctx.getChild(0).getSymbol().column, close_column[0])
        return self.visitChildren(ctx)
