package getScrapes;

import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.Reader;
import java.net.URL;
import java.net.URLConnection;
import java.util.ArrayList;
import java.util.HashSet;
import java.util.Set;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

//given region and location list, returns the sub-region the ad was posted from
public class reconstructSubRegion {

    public static void main(String args[]) throws IOException {
    	
    	String region = "chicago";
    	ArrayList<String> locations = new ArrayList<String>();
    	locations.add("Chicago");
    	locations.add("City of Chicago");
    	locations.add("New Delhi");
    	locations.add("South Delhi");
    	
    	//go to url	
    	String url = "http://posting." + region + 
    			".backpage.com/online/classifieds/PostAdPPI.html/"+region+
    			".backpage.com/?serverName="+region+
    			".backpage.com&category=4443&section=4381";
    	
    	//get the html scrape of that page
    	URL urlconnect = new URL(url);
    	URLConnection connection = urlconnect.openConnection(); 
        BufferedReader in = new BufferedReader
        		(new InputStreamReader(connection.getInputStream(), "UTF-8")); 
        String sourcetext = readAll(in);
        //System.out.println(sourcetext);
        
        //find the sub-regions
        ArrayList<String> subRegions = new ArrayList<String>();
        String pattern = "div class=\"jsChooser jsChooser_region\" data-superRegion=\"(.*)\" ";
        Pattern r = Pattern.compile(pattern);
        Matcher m = r.matcher(sourcetext);
        while (m.find()) {
        	for (int i = 1; i <= m.groupCount(); i++) {
        		//System.out.println(m.group(i));
        		subRegions.add(m.group(i));
        	}
        }
        
        //get the set of possible sub-regions
        Set<String> intersection = new HashSet<String>(locations);
        intersection.retainAll(subRegions);
        
        //check if the selected sub-region(s) has more options underneath
        ArrayList<String> moreOpt = new ArrayList<String>();
        boolean foundMoreOpt = false;
        for (String sR : intersection) {
        	String isMoreOpt = "data-superRegion=\""+sR+"\" data-multiple=\"yes\"";
        	if (sourcetext.contains(isMoreOpt)) {
        		foundMoreOpt = true;
        		//contains more options, so need to build a new sub-region list
        		String url2 = "http://posting." + region + 
        				".backpage.com/online/classifieds/PostAdPPI.html/" + region + 
        				".backpage.com/?&serverName="+region+
        				".backpage.com&superRegion="+sR+
        				"&section=4381&category=4443";
        		//get the html scrape of that page
            	URL urlconnect2 = new URL(url);
            	URLConnection connection2 = urlconnect2.openConnection(); 
                BufferedReader in2 = new BufferedReader
                		(new InputStreamReader(connection2.getInputStream(), "UTF-8")); 
                String start = "<div class=\"jsChooser jsChooser_region\" data-superRegion=\"" + sR +"\"";
                String end = "</div><!-- .chooseRegion -->";
                String sourcetext2 = readPart(in2,start,end);
                
                //get the list of more options
                String pattern2 = "[0-9]\">(.*)</a></li>";
                Pattern r2 = Pattern.compile(pattern2);
                Matcher m2 = r2.matcher(sourcetext2);
                while (m2.find()) {
                	for (int i = 1; i <= m2.groupCount(); i++) {
                		//System.out.println(m2.group(i));
                		moreOpt.add(m2.group(i));
                	}
                }
        	}	
        }
        
        //if found more options
        if (foundMoreOpt) {
        	Set<String> intersection2 = new HashSet<String>(locations);
        	intersection2.retainAll(moreOpt);
        	for (String sR : intersection2) System.out.println(sR);
        }
        
        else {
        	for (String sR : intersection) System.out.println(sR);
        }
    	 	
    }
    
    private static String readPart(Reader rd, String start, String end) throws IOException {
        StringBuilder sb = new StringBuilder();
        int cp;
        while ((cp = rd.read()) != -1) {
        	sb.append((char) cp);
        }
        String temp = sb.toString();
        int start_idx = temp.indexOf(start);
        int end_idx = temp.indexOf(end, start_idx);
        return temp.substring(start_idx, end_idx);
      }
    
    private static String readAll(Reader rd) throws IOException {
        StringBuilder sb = new StringBuilder();
        int cp;
        cp = rd.read();
        while ((cp = rd.read()) != -1) {
          sb.append((char) cp);
        }
        return sb.toString();
      }

}

