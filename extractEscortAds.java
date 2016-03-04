package getScrapes;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;

public class extractEscortAds {

    public static void main(String args[]) throws IOException {
    	String[] command = new String[]{"curl", "-u", "memex:qRJfu2uPkMLmH9cp", "-XGET",
    			"https://els.istresearch.com:19200/memex-domains/escorts/_search?size=1&from=27057019&pretty=true",
    	         "-d", "{ \"query\": { \"filtered\": { \"filter\": { \"term\": { \"url.domain\": \"backpage.com\" } } } } }"};
    	
    	//Pull out all ads within a given time span - Posted: \n    Tuesday, March 1, 2016 4:40 PM
    	//For each ad, get the following information: 
    	//(1) "_id" : "DD94E11245F344F1CBCBAA3664EFD0F3C6C268C7E876C8DF4925B62D369FA7C4"
    	// DD94E11245F344F1CBCBAA3664EFD0F3C6C268C7E876C8DF4925B62D369FA7C4
    	//(2) Location: \n        Des Moines, Outcall. Incall. Jordan Creek pkwy\n
    	// Des Moines
    	// Outcall
    	// Incall
    	// Jordan Creek pkwy
    	//(3) Post ID: 10857672 iowa\n
    	// 10857672
    	// iowa
    	
    	
    	 String output = executeCommand(command);
    	 System.out.println(output);    	
    }
    
    public static String executeCommand(String[] command) {
        StringBuffer output = new StringBuffer();

        Process p;
        try {
          p = Runtime.getRuntime().exec(command);
          BufferedReader reader = new BufferedReader(new InputStreamReader(
              p.getInputStream()));
          System.out.println(reader.readLine()); // value is NULL
          String line = "";
          while ((line = reader.readLine()) != null) {
            output.append(line + "\n");
          }
        } catch (Exception e) {
          e.printStackTrace();
        }
        return output.toString();
      }

}

