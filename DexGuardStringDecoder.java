import jeb.api.IScript;
import jeb.api.JebInstance;
import jeb.api.ast.*;
import jeb.api.ast.Class;
import jeb.api.dex.Dex;
import jeb.api.dex.DexCodeItem;
import jeb.api.dex.DexFieldData;
import jeb.api.dex.DexMethod;
import jeb.api.ui.JavaView;
import jeb.api.ui.View;

import java.util.List;

/**
 * Created by AKosterin on 29/06/15.
 */
public class DexGuardStringDecoder implements IScript{
    private static int encint = 0;
    private static String mname_decrypt = "";
    private static byte[] encbytes = new byte[0];

    public void run(JebInstance jebInstance) {
        jebInstance.print("DexGuardStringDecoder_Start");

        if(!jebInstance.isFileLoaded()){
            jebInstance.print("Please load a dex file");
            return;
        }

        Dex dex = jebInstance.getDex();
        JavaView view = (JavaView) jebInstance.getUI().getView(View.Type.JAVA);

        String methodname = view.getCodePosition().getSignature();
        jebInstance.print(methodname);

        DexCodeItem code = dex.getMethodData(methodname).getCodeItem();

        if(code == null){
            jebInstance.print("MethodData not found in DEX!!!");
            return;
        }

        jebInstance.decompileClass(getClassFromSignature(methodname));

        String str1 = getClassFromSignature(methodname);
        jebInstance.print(str1);

        Class mClass = jebInstance.getDecompiledClassTree(str1);
        for(Field mField : (List<Field>) mClass.getFields()){
            if(mField.getSignature().endsWith(":[B")) {
                jebInstance.print(mField.getSignature());
                DexFieldData dfd = dex.getFieldData(mField.getSignature());

                int wanted_flags = Dex.ACC_PRIVATE | Dex.ACC_STATIC | Dex.ACC_FINAL;
                if ((dfd.getAccessFlags() & wanted_flags) == wanted_flags) {
                    jebInstance.print("Found field:" + mField.getSignature());

                    int fIndex = dfd.getFieldIndex();

                    for (Integer mIndex : (List<Integer>) dex.getFieldReferences(fIndex)) {
                        DexMethod mMethod = dex.getMethod(mIndex);
                        if(mMethod.getSignature(true).contains("(III)Ljava/lang/String;")){
                            mname_decrypt = mMethod.getName();
                        }
                    }

                    for (Method method : (List<Method>) mClass.getMethods()) {
                        if (method.getName().equals("<clinit>")) {
                            for (int i = 0 ; i < method.getBody().size(); i++) {
                                Statement st1 = method.getBody().get(i);
                                if (st1 instanceof Assignment) {
                                    Assignment ass1 = (Assignment) st1;
                                    ILeftExpression le1 = ass1.getLeft();
                                    if ((le1 instanceof StaticField) && ((StaticField) le1).getField().getSignature().equals(mField.getSignature())) {
                                        IExpression e1 = ass1.getRight();
                                        if (e1 instanceof NewArray) {
                                            NewArray na1 = (NewArray) e1;
                                            for (IExpression e2 : ((List<IExpression>) na1.getInitialValues())) {
                                                if (e2 instanceof Constant) {
                                                    Constant c1 = (Constant) e2;
                                                    byte b1 = c1.getByte();
                                                    byte[] c = new byte[encbytes.length + 1];
                                                    System.arraycopy(encbytes, 0, c, 0, encbytes.length);
                                                    c[encbytes.length] = b1;
                                                    encbytes = c;
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            } else if(mField.getSignature().endsWith(":I")) {
                jebInstance.print(mField.getSignature());
                DexFieldData dfd = dex.getFieldData(mField.getSignature());

                int wanted_flags = Dex.ACC_PRIVATE | Dex.ACC_STATIC;
                if ((dfd.getAccessFlags() & wanted_flags) == wanted_flags) {
                    jebInstance.print("Found field:" + mField.getSignature());

                    for (Method method : (List<Method>) mClass.getMethods()) {
                        if (method.getName().equals("<clinit>")) {
                            for (int i = 0 ; i < method.getBody().size(); i++) {
                                Statement st1 = method.getBody().get(i);
                                if (st1 instanceof Assignment) {
                                    Assignment ass1 = (Assignment) st1;
                                    ILeftExpression le1 = ass1.getLeft();
                                    if ((le1 instanceof StaticField) && ((StaticField) le1).getField().getSignature().equals(mField.getSignature())) {
                                        IExpression e1 = ass1.getRight();
                                        if (e1 instanceof Constant) {
                                            Constant const1 = (Constant) e1;

                                            encint = const1.getInt();
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }

        if(encbytes.length == 0 ){
            jebInstance.print("Encrypted strings byte array not found");
        }

        if (mname_decrypt.isEmpty()){
            jebInstance.print("Decryption method was not found");
        }

        if(encint == 0 ){
            jebInstance.print("May be decrypt int was not found");
        }

        for(Method m : (List<Method>) mClass.getMethods()){
            jebInstance.print("Decrypting strings in method: " + m.getName());
            for (int i = 0; i < m.getBody().size(); i++) {
                Statement mStatement = m.getBody().get(i);

                checkElement(jebInstance, m.getBody(), mStatement, 0);
            }
        }

        jebInstance.getUI().getView(View.Type.JAVA).refresh();

        jebInstance.print("DexGuardStringDecoder_End");
    }

    private static void checkElement(JebInstance jebInstance,IElement parent, IElement iElement, int level){
        if (iElement instanceof Call){
            Call mCall = (Call) iElement;
            String methodName = mCall.getMethod().getName();
            if(methodName.equals(mname_decrypt)){
                int[] params = new int[0];
                StringBuilder strb = new StringBuilder();
                strb.append(methodName).append("(");
                for (IExpression mIExpression : (List<IExpression>) mCall.getArguments()) {
                    if (mIExpression instanceof Constant) {
                        Constant mConstant = (Constant) mIExpression;

                        params = addToIntArray(params, mConstant.getInt());

                        strb.append(mConstant.getInt()).append(", ");
                    } else if (mIExpression instanceof ArrayElt) {
                        ArrayElt mArrayElt = (ArrayElt) mIExpression;

                        IExpression mIExpression2 = mArrayElt.getIndex();

                        if (mIExpression2 instanceof Constant) {
                            Constant mConstant = (Constant) mIExpression2;

                            params = addToIntArray(params, (int) encbytes[mConstant.getInt()]);

                            strb.append(encbytes[mConstant.getInt()]).append(", ");
                        } else {
                            strb.append("encbytes[").append(mIExpression2.getClass().getName()).append("], ");
                        }
                    } else if(mIExpression instanceof StaticField) {
                        params = addToIntArray(params, encint);

                        strb.append(encint).append(", ");
                    } else if(mIExpression instanceof Expression){
                        Expression mExpression = (Expression) mIExpression;

                        if(mExpression.getLeft() != null) {

                            if (mExpression.getLeft() instanceof StaticField && mExpression.getRight() instanceof Constant) {
                                Constant mConstant = (Constant) mExpression.getRight();

                                int mint;

                                if(mExpression.getOperator().toString().equals("&")){
                                    mint = encint & mConstant.getInt();

                                    params = addToIntArray(params, mint);
                                    strb.append(mint).append(", ");
                                } else if(mExpression.getOperator().toString().equals("|")) {
                                    mint = encint | mConstant.getInt();
                                    params = addToIntArray(params, mint);
                                    strb.append(mint).append(", ");
                                } else if(mExpression.getOperator().toString().equals("-")) {
                                    mint = encint - mConstant.getInt();
                                    params = addToIntArray(params, mint);
                                    strb.append(mint).append(", ");
                                } else if(mExpression.getOperator().toString().equals("+")) {
                                    mint = encint + mConstant.getInt();
                                    params = addToIntArray(params, mint);
                                    strb.append(mint).append(", ");
                                } else if(mExpression.getOperator().toString().equals("*")) {
                                    mint = encint * mConstant.getInt();
                                    params = addToIntArray(params, mint);
                                    strb.append(mint).append(", ");
                                } else {
                                    strb.append(encint).append(" ").append(mExpression.getOperator().toString()).append(" ").append(mConstant.getInt()).append(", ");
                                }
                            } if (mExpression.getLeft() instanceof ArrayElt && mExpression.getRight() instanceof Constant) {
                                ArrayElt mArrayElt = (ArrayElt) mExpression.getLeft();
                                Constant mConstant = (Constant) mExpression.getRight();

                                IExpression mIExpression2 = mArrayElt.getIndex();

                                if (mIExpression2 instanceof Constant) {
                                    Constant mConstant2 = (Constant) mIExpression2;

                                    int mint;

                                    if(mExpression.getOperator().toString().equals("&")) {
                                        mint = encbytes[mConstant2.getInt()] & mConstant.getInt();
                                        params = addToIntArray(params, mint);
                                        strb.append(mint).append(", ");
                                    } else if(mExpression.getOperator().toString().equals("|")){
                                        mint = encbytes[mConstant2.getInt()] | mConstant.getInt();
                                        params = addToIntArray(params, mint);
                                        strb.append(mint).append(", ");
                                    } else if(mExpression.getOperator().toString().equals("-")){
                                        mint = encbytes[mConstant2.getInt()] - mConstant.getInt();
                                        params = addToIntArray(params, mint);
                                        strb.append(mint).append(", ");
                                    } else if(mExpression.getOperator().toString().equals("+")){
                                        mint = encbytes[mConstant2.getInt()] + mConstant.getInt();
                                        params = addToIntArray(params, mint);
                                        strb.append(mint).append(", ");
                                    } else if(mExpression.getOperator().toString().equals("*")){
                                        mint = encbytes[mConstant2.getInt()] * mConstant.getInt();
                                        params = addToIntArray(params, mint);
                                        strb.append(mint).append(", ");
                                    } else {
                                        strb.append(encbytes[mConstant2.getInt()]).append(" ").append(mExpression.getOperator().toString()).append(" ").append(mConstant.getInt()).append(", ");
                                    }
                                } else {
                                    strb.append("jeb.api.ast.Expression(").append(mExpression.getLeft().getClass().getName()).append(" ").append(((Expression) mIExpression).getOperator().getClass().getName()).append(" ").append(mExpression.getRight().getClass().getName()).append("), ");
                                }
                            } else {
                                strb.append("jeb.api.ast.Expression(").append(mExpression.getLeft().getClass().getName()).append(" ").append(((Expression) mIExpression).getOperator().getClass().getName()).append(" ").append(mExpression.getRight().getClass().getName()).append("), ");
                            }
                        } else {
                            if(mExpression.getRight() instanceof ArrayElt){
                                ArrayElt mArrayElt = (ArrayElt) mExpression.getRight();

                                IExpression mIExpression2 = mArrayElt.getIndex();

                                if (mIExpression2 instanceof Constant) {
                                    Constant mConstant = (Constant) mIExpression2;

                                    params = addToIntArray(params, -1 * encbytes[mConstant.getInt()]);

                                    strb.append(-1 * encbytes[mConstant.getInt()]).append(", ");
                                } else {
                                    strb.append("jeb.api.ast.Expression(").append(((Expression) mIExpression).getOperator().getClass().getName()).append(" ").append(mExpression.getRight().getClass().getName()).append("), ");
                                }
                            } else {
                                strb.append("jeb.api.ast.Expression(").append(((Expression) mIExpression).getOperator().getClass().getName()).append(" ").append(mExpression.getRight().getClass().getName()).append("), ");
                            }

                        }


                    } else {
                        strb.append(mIExpression.getClass().getName()).append(", ");
                    }
                }

                strb.delete(strb.length() - 2, strb.length());

                strb.append(");");

                if (params.length == 3){
                    String decyptStr = decrypt_djAR(params[0], params[1], params[2]);
                    strb.append(" - ").append(decyptStr);
                    parent.replaceSubElement(iElement, (new Constant.Builder(jebInstance)).buildString(decyptStr));
                }

                jebInstance.print(strb.toString());
            }
        }

        for (IElement element : (List<IElement>) iElement.getSubElements()){
            if (!((element instanceof Class) || (element instanceof Field) || (element instanceof Method))){
                checkElement(jebInstance, iElement, element, level + 1);
            }
        }
    }

    private static final String getClassFromSignature(String sig) {
        return sig.split(";")[0].split("$")[0] + ";";//
    }

    private static final int[] addToIntArray(int[] array, int mint){
        int[] array2 = new int[array.length + 1];
        System.arraycopy(array, 0, array2, 0, array.length);
        array2[array.length] = mint;
        return array2;
    }
    
    
    //Could be determined by analyzing the decryption method
    private static final String decrypt_djAR(int arg9, int arg10, int arg11) {
        int v5;
        byte[] v6 = encbytes;
        int v1 = arg10 + 65;
        int v0 = 615 - arg9;
        int v3 = arg11 + 2;
        byte[] v2 = new byte[v3];
        int v8 = v3 - 1;
        v3 = 0;
        v5 = v0;
        while(v3 != v8){
            v2[v3] = ((byte)v1);
            v0 = v6[v5];
            ++v3;
            ++v5;
            v1 += -v0;

        }

        v2[v3] = ((byte)v1);
        return new String(v2);
    }
}
