package getScrapes;

import java.io.File;
import java.io.FileWriter;
import java.io.IOException;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.logging.FileHandler;
import java.util.logging.Logger;
import java.util.logging.SimpleFormatter;

import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;
import org.openqa.selenium.By;
import org.openqa.selenium.Proxy;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.remote.CapabilityType;
import org.openqa.selenium.remote.DesiredCapabilities;

import edu.berkeley.nlp.util.Pair;

public class scrapeLA {

	static String PROXY = "localhost:30002";
	static Proxy proxy = new Proxy();
	 
	  //Use Capabilities when launch browser driver Instance.
	  
	static WebDriver driver = new FirefoxDriver();
	static String directory = "scrapes/";
	private static Logger logger = Logger.getLogger(scrapeLA.class.getName());
	
    public static void main(String args[]) throws IOException, InterruptedException, ClassNotFoundException {
    	
    	
    	proxy.setHttpProxy(PROXY).setFtpProxy(PROXY).setSslProxy(PROXY).setSocksProxy(PROXY);
  	  	DesiredCapabilities cap = new DesiredCapabilities();
  	  	cap.setCapability(CapabilityType.PROXY, proxy);
  	  	driver = new FirefoxDriver(cap);
  	
  		ArrayList<String> languages = new ArrayList<String>();
    	languages.add("english");
    	    	

    	long ts = System.currentTimeMillis();
    	File folder = new File(directory+"LA_"+ts+"/");
		if (!folder.exists()) folder.mkdir();
		
		FileHandler fh = new FileHandler(directory+"log_"+ts+".txt"); 
		logger.addHandler(fh);
        SimpleFormatter formatter = new SimpleFormatter();  
        fh.setFormatter(formatter); 
        logger.setUseParentHandlers(false);
    	
    	for (String language : languages) {
    		
	    	Pair<ArrayList<String>, String> data = getServices(language);
	    	ArrayList<String> services = data.getFirst();
	    	String data_input = data.getSecond();
	    	
	    	for (String service : services) {
	    		//System.out.println(service);
	    		logger.info(service); 
	    		getCityToPrice(service, "la", data_input, language, ts, logger);
	    	}
    	}
    	driver.close();

    }
    
    public static void getCityToPrice(String service, String region, 
    		String data_input, String language, long ts, Logger logger) throws IOException, InterruptedException {
    	
    	String[] data_input_asArray = data_input.split("[|]");
    	String data_name = data_input_asArray[0];
    	String data_continue = data_input_asArray[1];
    	String data_login = data_input_asArray[2];
    	/*System.out.println(data_name);
    	System.out.println(data_continue);
    	System.out.println(data_login);*/
    	String tag = "com";
    	if (language.equals("mexico")) tag = "mx";
    	
    	HashMap<String, Double> city_price = new HashMap<String, Double>();
    	
    	/*** get the true shorthand for the region ***/
    	Document d0;
    	try {
    		d0 = Jsoup.connect("http://"+region +".backpage."+tag).timeout(0).get();
    	}
    	catch(java.net.UnknownHostException|org.jsoup.HttpStatusException e){
    		Thread.sleep(5000);
    		d0 = Jsoup.connect("http://"+region +".backpage."+tag).timeout(0).get();
    	}
    	
    	Elements links0 = d0.select("a");
    	for (Element link : links0) {
    		String check = link.attr("href");
    		//System.out.println(check);
    		if (check.contains("/classifieds/AllCities")) {
    			int s_index = check.indexOf("http://");
    			int e_index = check.indexOf(".backpage");
    			region = check.substring(s_index+7, e_index);
    			break;
    		}
    	}
    	/***/
    	
    	/*** get the url with specified service and region***/
    	String bUrl = "http://posting."+region+".backpage."+tag;
    	String zeroUrl = bUrl + "/online/classifieds/PostAdPPI.html/";
    	Document d_;
    	try {
    		d_ = Jsoup.connect(zeroUrl).timeout(0).get();
    	}
    	catch(org.jsoup.HttpStatusException e){
    		Thread.sleep(5000);
    		try{
    			d_ = Jsoup.connect(zeroUrl).timeout(0).get();
    		}
    		catch(org.jsoup.HttpStatusException f) {
    			Thread.sleep(5000);
    			d_ = Jsoup.connect(zeroUrl).timeout(0).get();
    		}
    	}
    	//Document d = Jsoup.connect(zeroUrl).get();
    	Elements links_ = d_.select("a");
    	String firstUrl = bUrl;
    	for (Element link : links_) {
    		if (link.attr("data-name").equals(data_name)) {
    			firstUrl += link.attr("href");
    			break;
    		}
    	}

    	Document d2;
    	try {
    		d2 = Jsoup.connect(firstUrl).timeout(0).get();
    	}
    	catch(org.jsoup.HttpStatusException e) {
    		Thread.sleep(5000);
    		d2 = Jsoup.connect(firstUrl).timeout(0).get();
    	}
    	//Document d2 = Jsoup.connect(firstUrl).timeout(0).get();
    	Elements links2 = d2.select("a");
    	String locsUrl = bUrl;
    	for (Element link : links2) {
    		String serv = link.attr("data-name");
    		//System.out.println(serv);
    		if (serv.equals("strippers & strip clubs")) {
    			serv = "strippers/strip clubs";
    		}
    		if (serv.equals(service)) {
    			locsUrl += link.attr("href");
    			break;
    		}
    	}
    	/***/
    
    	String url = locsUrl;
    	
    	//System.out.println("first post page : " + url);
    	//WebDriver driver = new FirefoxDriver();
    	Document d;
    	try {
    		d = Jsoup.connect(url).timeout(0).get();
    	}
    	catch(java.net.UnknownHostException|org.jsoup.HttpStatusException e){
    		Thread.sleep(5000);
    		d = Jsoup.connect(url).timeout(0).get();
    	}
    	Elements links = d.select("a");
    	
    	ArrayList<String> nextUrls = new ArrayList<String>();
    	//String nextUrl = url;
    	
    	String baseUrl = "http://posting."+region +".backpage."+tag;
    	int count = 0;
    	for (Element link : links) {
    		String check = baseUrl+link.attr("href");
    		//System.out.println(check);
    		if (check.contains("superRegion")) {// && link.attr("data-name").equals(service)) {
    			nextUrls.add(check);// = check;
    			//break;
    			count++;
    			if (count == 9) break;
    		}
    	}
    	
    	for (String nextUrl : nextUrls) {
    		
    		String chunk = "http://posting.la.backpage.com/online/classifieds/PostAdPPI.html"
    				+ "/?serverName=la.backpage.com&superRegion=";
    		int pos = nextUrl.indexOf(chunk) + chunk.length();
    		int pos2 = nextUrl.indexOf("&", pos);
    		String name = nextUrl.substring(pos, pos2).replace("%20", " ");
    		//System.out.println(name);
    		logger.info(name);
    		//System.out.println(nextUrl);
    	
    	//System.out.println("potential click page: " + nextUrl);
    	String nextUrl_inner = "";
    	
    	driver.get(nextUrl);
    	Thread.sleep(1000);
		try {
			String a = "//input[@class='button'][contains(@value,'"+data_continue+"')]";
			if (language == "spanish" || language == "mexico") {
				List<WebElement> buttons = driver.findElements(By.xpath(a));
				for (WebElement button : buttons) {
					if (button.getAttribute("value").equals("Publicar")) {
						button.click();
						break;
					}
				}
			}
			else {
				driver.findElement(By.xpath(a)).click();
			}
		}
		catch (org.openqa.selenium.NoSuchElementException e) {
			driver.close();
			Thread.sleep(5000);
			driver = new FirefoxDriver();
			driver.get(nextUrl);
			try {
				WebElement BUTTON = null;
				String a = "//input[@class='button'][contains(@value,'"+data_continue+"')]";
				if (language == "spanish" || language == "mexico") {
					List<WebElement> buttons = driver.findElements(By.xpath(a));
					for (WebElement button : buttons) {
						if (button.getAttribute("value").equals("Publicar")) {
							BUTTON = button;
							//button.click();
							break;
						}
					}
				}
				else {
					BUTTON = driver.findElement(By.xpath(a));
					//driver.findElement(By.xpath(a)).click();
				}
				BUTTON.click();
				//driver.findElement(By.xpath("//input[@class='button'][contains(@value,'Continue')]")).click();
				}
			catch (org.openqa.selenium.NoSuchElementException e1) {
				driver.close();
				Thread.sleep(5000);
				driver = new FirefoxDriver();
				driver.get(nextUrl);
				try {
					String a = "//input[@class='button'][contains(@value,'"+data_continue+"')]";
					if (language == "spanish" || language == "mexico") {
						List<WebElement> buttons = driver.findElements(By.xpath(a));
						for (WebElement button : buttons) {
							if (button.getAttribute("value").equals("Publicar")) {
								button.click();
								break;
							}
						}
					}
					else {
						driver.findElement(By.xpath(a)).click();
					}
					//driver.findElement(By.xpath("//input[@class='button'][contains(@value,'Continue')]")).click();
					}
				catch (org.openqa.selenium.NoSuchElementException e2) {
					//System.out.println("sorry! failed to find submit button");
					logger.info("sorry! failed to find submit button");
				}
				catch (org.openqa.selenium.ElementNotVisibleException e2) {
					//System.out.println("sorry! failed to see submit button");
					logger.info("sorry! failed to see submit button");
				}
			}
			catch (org.openqa.selenium.ElementNotVisibleException e1) {
				driver.close();
				Thread.sleep(5000);
				driver = new FirefoxDriver();
				driver.get(nextUrl);
				try {
					String a = "//input[@class='button'][contains(@value,'"+data_continue+"')]";
					if (language == "spanish" || language == "mexico") {
						List<WebElement> buttons = driver.findElements(By.xpath(a));
						for (WebElement button : buttons) {
							if (button.getAttribute("value").equals("Publicar")) {
								button.click();
								break;
							}
						}
					}
					else {
						driver.findElement(By.xpath(a)).click();
					}
					//driver.findElement(By.xpath("//input[@class='button'][contains(@value,'Continue')]")).click();
					}
				catch (org.openqa.selenium.NoSuchElementException e2) {
					//System.out.println("sorry! failed to find submit button");
					logger.info("sorry! failed to find submit button");
				}
				catch (org.openqa.selenium.ElementNotVisibleException e2) {
					//System.out.println("sorry! failed to see submit button");
					logger.info("sorry! failed to see submit button");
				}
			}
			//driver.findElement(By.xpath("//input[@class='button'][contains(@value,'Continue')]")).click();
		}
		catch (org.openqa.selenium.ElementNotVisibleException e) {
			//System.out.println("ELEMENT NOT VISIBLE");
			//button not there
			driver.close();
			Thread.sleep(5000);
			driver = new FirefoxDriver();
			Document d_inner = Jsoup.connect(url).timeout(0).ignoreHttpErrors(true).get();
			//System.out.println(d_inner);
			Elements links_inner = d_inner.select("a");
			for (Element link : links_inner) {
				String option = link.attr("data-region");
				if (option.equals("")) continue;
				
	    		String check = baseUrl+link.attr("href");
	    		//System.out.println(check);
	    		String no_percent = check.replace("%20", " ");
	    		if (check.contains("superRegion") && no_percent.contains(name)) {//&& link.attr("data-name").equals(service)) {
	    			nextUrl_inner = check;
	    			//System.out.println(nextUrl_inner);
	    			break;
	    		}
	    	}
			driver.get(nextUrl_inner);
			//System.out.println(nextUrl_inner);
			Thread.sleep(5000);
			try {
				String a = "//input[@class='button'][contains(@value,'"+data_continue+"')]";
				if (language == "spanish" || language == "mexico") {
					List<WebElement> buttons = driver.findElements(By.xpath(a));
					for (WebElement button : buttons) {
						if (button.getAttribute("value").equals("Publicar")) {
							button.click();
							break;
						}
					}
				}
			
				else {
					driver.findElement(By.xpath(a)).click();
				}
			}
			catch (org.openqa.selenium.NoSuchElementException e2) {
				//System.out.println("sorry! failed to find submit button");
				logger.info("sorry! failed to find submit button");
			}
			catch (org.openqa.selenium.ElementNotVisibleException e2) {
				//System.out.println("sorry! failed to see submit button");
				logger.info("sorry! failed to see submit button");
			}
			//driver.findElement(By.xpath("//input[@class='button'][contains(@value,'Continue')]")).click();
		}
		
		//if ((!nextUrl_inner.equals(""))) System.out.println("def click page: " + nextUrl_inner);
		//else System.out.println("def click page: " + nextUrl);
		
		Thread.sleep(2000);
		try {
			String a = "//input[@class='signIn'][contains(@value,'"+data_login+"')]";

			driver.findElement(By.id("centralEmail")).sendKeys("backpage.uc@gmail.com");
			driver.findElement(By.id("centralPassword")).sendKeys("r3s34rch");
			driver.findElement(By.xpath(a)).click();
			//driver.findElement(By.xpath("//input[@class='signIn'][contains(@value,'Login')]")).click();	
		}
		catch (org.openqa.selenium.NoSuchElementException e) {
			//System.out.println("no login found");
			logger.info("no login found");
		}
		
		//Thread.sleep(5000);
		
		String html = driver.getPageSource();
		//Document parsed_html = Jsoup.parse(html);
		
		if (!html.equals("")) {
        	File file = new File(directory+"/LA_"+ts+"/"+service.replace("/", "")+"_"+name+"_"+System.currentTimeMillis()+".txt");
        	file.createNewFile();
        	FileWriter fileWriter = new FileWriter(file);
        	fileWriter.write(html);
        	fileWriter.flush();
        	fileWriter.close();
		}
    	}
		//return html;
    	
    }
    
   public static Pair<ArrayList<String>,String> getServices(String language) {
	   ArrayList<String> services = new ArrayList<String>();
	   String data_name = "";
	   if (language == "english") {
       		services.add("adult jobs");
       		services.add("body rubs");
       		services.add("domination & fetish");
       		services.add("escorts");
       		services.add("male escorts");
       		services.add("phone & websites");
       		services.add("strippers/strip clubs");
       		services.add("transsexual escorts");
		   data_name = "adult entertainment|Continue|Login";
		   }	
	   return new Pair<ArrayList<String>, String>(services, data_name);
   }
}