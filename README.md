## JEB Python scripts
- [HelloWorld.py](HelloWorld.py)
    - Display message box.
- [ListingMethods.py](ListingMethods.py)
    - Print all methods in dex.
- [InvokedMethods.py](InvokedMethods.py)
    - Get caret position and print invoked methods from it.
- [RenameObfuscatedClasses.py](RenameObfuscatedClasses.py)
    - Rename obfuscated class names by using super class name. 
- [AlertMarker.py](AlertMarker.py)
    - Set(unset) alert marker to focused method.
- [getMethodSignatures.py](getMethodSignatures.py)
    - Get method signatures from an APK and store them into a text file for parsing it later on.   (Use the Java version)  
- [getMethodsFromClass.py](getMethodsFromClass.py)
    - Get method from a class and print them out. 
- [ASTRemoveDummySwitch.py](ASTRemoveDummySwitch.py)
    - Remove dummy switches
- [ObadDecrypt.py](ObadDecrypt.py)
    - Decrypt Obad strings before performing unreflection
- [ObadUnreflect.py](ObadUnreflect.py)
    - Replace reflection calls by direct method calls
- [fixObfousClass.py](fixObfousClass.py)
    - Rename obfuscated class name with source name. (fr0zenrain)
          
      ![imaing](https://bytebucket.org/dudux/jebscripts/raw/ecf2962bebeedfcbef918a42f989e860fe939205/snapshot.png)

      Recover android dex's class name obfouscator by proguard with "-keepattributes SourceFile". 
      Most app need save the crash log, so the do not clear source name,maybe some nest class can not fix.

## JEB Java scripts
- [DeCluster.java](DeCluster.java)
    - Renaming obfuscated class/methods/fields names (@jcase)
- [DeClusterMod.java](DeClusterMod.java)
    - Renaming obfuscated class/methods/fields names with filter and string format added
- [DexGuardStringDecoder.java](DexGuardStringDecoder.java)
    - Decrypt DexGuard encrypted Strings (Anton Kosterin)
- [getMethodSignatures.java](getMethodSignatures.java)
    - Get method signatures from an APK and store them into a text file for parsing it later on.
 

## Extra Python scripts
- [grepDeobfuscationRoutines.py](grepDeobfuscationRoutines.py)
    - Filter possible obfuscator routines from a method signatures list (First use getMethodSignatures.java)

# JEB Sample Scripts
Sample automation scripts for [JEB(Android Interactive Decompiler)](http://www.android-decompiler.com/index.php).

## Usage
Usage of JEB automation is [here](http://www.android-decompiler.com/manual.php#automation).

JEB API reference is [here](http://www.android-decompiler.com/apidoc/).



