/**
? name=DeCluster v1.1.3, help=This Java file is a JEB plugin

1.1.3 Add string.format for classes names
1.1.2 @jcase
*/
import jeb.api.IScript;
import jeb.api.JebInstance;
import jeb.api.dex.Dex;
import jeb.api.dex.DexField;
import jeb.api.ui.View;
import java.util.List; 


public class DeClusterMod implements IScript {
    int showErrors     = 0;  // Show errors, slows the plugin down greatly.
    int renameShort    = 1;  // Rename short names, such as a, Ab, AbC
    int renameAll      = 0;  // Renames all classes, regardless if the match the isValid rules
    int renameNonLatin = 1;  // Rename classes using non-latin chars
    int smartRename    = 1;  // Rename classes based on their type /not implemented/

    @SuppressWarnings("unchecked")
    public void run(JebInstance jeb) {
        jeb.print("DeCluster Plugin v1.1.3");
        jeb.print("By jcase@cunninglogic.com");
        jeb.print("Small Mods by @enovella_");

		String classPre      = "Class_";
		String innerPre      = "InnerClass_";
		String fieldPre      = "Field_";
		String methodPre     = "Method_";
		
		String classService  = "Service_";
		String classReceiver = "Receiver_";
		String classActivity = "Activity_";



        if (showErrors == 0) {
            jeb.print("Show Errors is disabled");
        }  else {
            jeb.print("Show Errors is enabled, this slows the script down!");
        }

        int count = 0;

        if  (!jeb.isFileLoaded()) {

            jeb.print("Please load a dex file");

        } else {
            
            jeb.print("Renaming fields..."); 
            List<String> myArr = jeb.getDex().getFieldSignatures(true);
            for (int i = myArr.size()-1; i >= 0; i--) { 
                String fieldName = myArr.get(i);

                if (!isValid(fieldName.substring(fieldName.indexOf(">")+1, fieldName.indexOf(":")))) {
                    ++count;
                    	
                        
                        try {
                        if(!jeb.setFieldComment(fieldName, "Renamed from " +fieldName)) {
                            if (showErrors != 0)
                                jeb.print("Error commenting field " + fieldName);
                        }
                        if(!jeb.renameField(fieldName,fieldPre + String.format("%05d", count))) {
                            if (showErrors != 0)
                                jeb.print("Error renaming field " + fieldName);
                        }

                    } catch(NullPointerException e) {
                        if (showErrors != 0)
                            jeb.print(e.toString() + " when renaming" + fieldName);

                    } catch(RuntimeException e) {
                        if (showErrors != 0)
                            jeb.print(e.toString() + " when renaming" + fieldName);

                    }
                }
                
            }

            count = 0;
            myArr.clear();

            jeb.print("Renaming methods..."); 
            myArr = jeb.getDex().getMethodSignatures(true);
             for (int i = myArr.size()-1; i >= 0; i--) { 
                String methodName = myArr.get(i);

                if (!isValid(methodName.substring(methodName.indexOf(">")+1, methodName.indexOf("(")))) {
                  
                        ++count;

                        
                        try {
                            if(!jeb.setMethodComment(methodName, "Renamed from " +methodName)) {
                                if (showErrors != 0)
                                    jeb.print("Error commenting method " + methodName);
                            }
                            if(!jeb.renameMethod(methodName,methodPre + String.format("%05d", count))) {
                                if (showErrors != 0)
                                    jeb.print("Error renaming method " + methodName);
                            }

                        } catch(NullPointerException e) {
                            if (showErrors != 0)
                                jeb.print(e.toString() + " when renaming" + methodName);

                        } catch(RuntimeException e) {
                            if (showErrors != 0)
                                jeb.print(e.toString() + " when renaming" + methodName);

                        }


                }
                
            }

            count = 0;
            myArr.clear();

            jeb.print("Renaming classes..."); 
            myArr = jeb.getDex().getClassSignatures(true);

            for (int i = myArr.size()-1; i >= 0; i--) { 
                String className = myArr.get(i);
                
                /** Modification */
                if (className.contains("com.add.your.package.to.blacklist.right.here") || className.contains("android/support/"))  {
                	if (showErrors != 0)
                		jeb.print(className + " is skipped!");
                	continue;
                }
                /**              */
                
                if (!isValid(className.substring(className.lastIndexOf("/")+1, className.length()-1))) {
                    ++count;

                    try {

                        if(!jeb.setClassComment(className, "Renamed from " +className)) {
                            if (showErrors != 0)
                               jeb.print("Error commenting class " + className);
                        }


                        if (className.contains("$")) {
                            if(!jeb.renameClass(className,innerPre + String.format("%05d", count))) {
                                if (showErrors != 0)
                                    jeb.print("Error renaming class " + className);
                            }
                        } else {
                            if(!jeb.renameClass(className,classPre + String.format("%05d", count))) {
                                if (showErrors != 0)
                                    jeb.print("Error renaming class " + className);
                            }
                        }

                    } catch(NullPointerException e) {
                        if (showErrors != 0)
                            jeb.print(e.toString() + " when renaming" + className);

                    } catch(RuntimeException e) {
                        if (showErrors != 0)
                            jeb.print(e.toString() + " when renaming" + className);

                    }
                }
                
            }

            jeb.getUI().getView(View.Type.CLASS_HIERARCHY).refresh();
            jeb.getUI().getView(View.Type.ASSEMBLY).refresh();
            jeb.print("Finished Renaming"); 
        }

    }

    public boolean isValid (String name){
        // This needs work 

        // Handle inner classes
        if (name.contains("$"))
            name.equals(name.replace("$",""));

        // Trying to do away with null pointers in method comments, not working.
        if (name == null || name.length() == 0 || name.contains("<init>") || name.contains("<clinit>"))
            return true;

        // Rename all classes
        if (renameAll != 0)
            return false;
            
        // Rename short class names, like output from ProGuard/Allatori
        if (renameShort != 0 && name.length() <= 3)
            return false;

        // Rename classes using non-latin chars
        if (renameNonLatin != 0 && !name.matches("\\w+"))
            return false;
            
        return true;
    }

}
