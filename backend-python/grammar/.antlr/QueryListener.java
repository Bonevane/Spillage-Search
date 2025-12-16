// Generated from d:/Spillage-Search/backend-python/grammar/Query.g4 by ANTLR 4.13.1
import org.antlr.v4.runtime.tree.ParseTreeListener;

/**
 * This interface defines a complete listener for a parse tree produced by
 * {@link QueryParser}.
 */
public interface QueryListener extends ParseTreeListener {
	/**
	 * Enter a parse tree produced by {@link QueryParser#query}.
	 * @param ctx the parse tree
	 */
	void enterQuery(QueryParser.QueryContext ctx);
	/**
	 * Exit a parse tree produced by {@link QueryParser#query}.
	 * @param ctx the parse tree
	 */
	void exitQuery(QueryParser.QueryContext ctx);
	/**
	 * Enter a parse tree produced by {@link QueryParser#orExpression}.
	 * @param ctx the parse tree
	 */
	void enterOrExpression(QueryParser.OrExpressionContext ctx);
	/**
	 * Exit a parse tree produced by {@link QueryParser#orExpression}.
	 * @param ctx the parse tree
	 */
	void exitOrExpression(QueryParser.OrExpressionContext ctx);
	/**
	 * Enter a parse tree produced by {@link QueryParser#andExpression}.
	 * @param ctx the parse tree
	 */
	void enterAndExpression(QueryParser.AndExpressionContext ctx);
	/**
	 * Exit a parse tree produced by {@link QueryParser#andExpression}.
	 * @param ctx the parse tree
	 */
	void exitAndExpression(QueryParser.AndExpressionContext ctx);
	/**
	 * Enter a parse tree produced by the {@code NotAtom}
	 * labeled alternative in {@link QueryParser#atom}.
	 * @param ctx the parse tree
	 */
	void enterNotAtom(QueryParser.NotAtomContext ctx);
	/**
	 * Exit a parse tree produced by the {@code NotAtom}
	 * labeled alternative in {@link QueryParser#atom}.
	 * @param ctx the parse tree
	 */
	void exitNotAtom(QueryParser.NotAtomContext ctx);
	/**
	 * Enter a parse tree produced by the {@code ParenAtom}
	 * labeled alternative in {@link QueryParser#atom}.
	 * @param ctx the parse tree
	 */
	void enterParenAtom(QueryParser.ParenAtomContext ctx);
	/**
	 * Exit a parse tree produced by the {@code ParenAtom}
	 * labeled alternative in {@link QueryParser#atom}.
	 * @param ctx the parse tree
	 */
	void exitParenAtom(QueryParser.ParenAtomContext ctx);
	/**
	 * Enter a parse tree produced by the {@code WordAtom}
	 * labeled alternative in {@link QueryParser#atom}.
	 * @param ctx the parse tree
	 */
	void enterWordAtom(QueryParser.WordAtomContext ctx);
	/**
	 * Exit a parse tree produced by the {@code WordAtom}
	 * labeled alternative in {@link QueryParser#atom}.
	 * @param ctx the parse tree
	 */
	void exitWordAtom(QueryParser.WordAtomContext ctx);
}