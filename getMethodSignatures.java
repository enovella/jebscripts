import jeb.api.IScript;
/*import jeb.api.ui.View;*/
import jeb.api.dex.Dex;
import jeb.api.JebInstance;
import java.util.*;
import java.io.*;

public class getMethodSignatures implements IScript {
    
    private static String path = "/tmp/methodsignatures.txt";

    public void run(JebInstance jeb){
        Dex dex  = jeb.getDex();
        List<String> methodSigList = new ArrayList<String>();

        methodSigList = dex.getMethodSignatures(true);

        try{
        	File file = new File(path);
	        FileOutputStream fos =  new FileOutputStream(file);
	        
	        for (String method : methodSigList)
	        	fos.write((method + "\n").getBytes());	            
        }catch(Exception e){
        	
        }

        jeb.print("[+] Output file located at "+path);
        jeb.print("[+] Done!");
    }

}
