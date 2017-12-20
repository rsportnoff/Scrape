package getScrapes;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileInputStream;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.FileWriter;
import java.io.IOException;
import java.io.InputStreamReader;
import java.io.ObjectInputStream;
import java.io.ObjectOutputStream;
import java.io.Reader;
import java.net.URL;
import java.net.URLConnection;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.HashMap;
import java.util.HashSet;
import java.util.List;
import java.util.Map;
import java.util.Set;
import java.util.concurrent.TimeUnit;
import java.util.logging.FileHandler;
import java.util.logging.Logger;
import java.util.logging.SimpleFormatter;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

//import org.json.JSONObject;
//import org.json.simple.parser.JSONParser;
//import org.json.simple.parser.ParseException;
//import org.jsoup.Connection;
//import org.jsoup.Connection.Method;
import org.jsoup.Jsoup;
import org.jsoup.nodes.Document;
import org.jsoup.nodes.Element;
import org.jsoup.select.Elements;
import org.openqa.selenium.By;
import org.openqa.selenium.WebDriver;
import org.openqa.selenium.WebElement;
import org.openqa.selenium.chrome.ChromeDriver;
import org.openqa.selenium.firefox.FirefoxDriver;
import org.openqa.selenium.support.ui.ExpectedConditions;
import org.openqa.selenium.support.ui.WebDriverWait;

import edu.berkeley.nlp.util.Pair;
import static java.util.Arrays.asList;

public class scrapePriceInfo5_escort {

	static WebDriver driver = new FirefoxDriver();
	private static Logger logger = Logger.getLogger(scrapePriceInfo5_escort.class.getName());

	//static HashSet<String> done = new HashSet<String>();
    public static void main(String args[]) throws IOException, InterruptedException, ClassNotFoundException {
    	
    	ArrayList<String> languages = new ArrayList<String>();
    	languages.add("us_edit");
    	/*languages.add("english");
    	languages.add("czech");
    	languages.add("danish");
    	languages.add("dutch");
    	languages.add("french");
    	languages.add("german");
    	languages.add("greek");
    	languages.add("hungarian");
    	languages.add("italian");
    	languages.add("norweigan");
    	languages.add("polish");
    	languages.add("portuguese");
    	languages.add("russian");
    	languages.add("spanish");
    	languages.add("mexico");
    	languages.add("turkish");*/
    	//languages.add("english");
    	
    	boolean seen_eng = false;
    	String currency = "$";
    	
    	long ts = System.currentTimeMillis();
    	File folder = new File("final_scrape/USA_"+ts+"_ESCORT/");
		if (!folder.exists()) folder.mkdir();
		
		FileHandler fh = new FileHandler("final_scrape/USA_"+ts+"_ESCORT/log.txt");
		logger.addHandler(fh);
        SimpleFormatter formatter = new SimpleFormatter();  
        fh.setFormatter(formatter); 
        logger.setUseParentHandlers(false);
    			
    	for (String language : languages) {
    		
    		//get the currency, data-name and list of services
    		//if (language == "english" && seen_eng == true) currency = "£";
    		//else if (language == "english" && seen_eng == false) seen_eng = true;
    		//currency = "£";
    		Pair<ArrayList<String>, String> data = getServices(language);
	    	ArrayList<String> services = data.getFirst();
	    	String data_input = data.getSecond();
	    	
	    	//Get the regions
	    	ArrayList<String> regions = new ArrayList<String>();
	    	String region_file = "final_scrape/regions_"+currency+language+".txt";
			BufferedReader rf_reader = new BufferedReader(new FileReader(region_file));
	    	String reg = rf_reader.readLine().trim().toLowerCase();
	    	regions.add(reg);
	    	
	    	reg = rf_reader.readLine();
	    	while (reg != null) {
	    		reg = reg.trim().toLowerCase();
	    		regions.add(reg);
	    		reg = rf_reader.readLine();
	    	}
	    	rf_reader.close();
	    	
	    	//for (String service : services) {
	    	int count = 0;
	    	outerloop:
	    	for (String region : regions) {
	    		count++;
	    		//done = new HashSet<String>();
	    		/*for (String c : done) {
	    			//System.out.println(c);
	    			if (c.toLowerCase().contains(region)) {
	    				//System.out.println("FOUND IT");
	    				continue outerloop;
	    			}
	    		}*/
	    		folder = new File("final_scrape/USA_"+ts+"_ESCORT/"+region+"/");
	    		if (!folder.exists()) folder.mkdir();
	    		
	    		//System.out.println(service);
	    		logger.info("On region " + count + " " + region);
	    		
	    		//int count = 0;
	    		//for (String region : regions) {
	    		for (String service : services) {
	    			count++;
	    			logger.info(service);
	    			folder = new File("final_scrape/USA_"+ts+"_ESCORT/"+region+"/"+service.replace("/", "")+"/");
		    		if (!folder.exists()) folder.mkdir();
	    			//System.out.println("On region " + count + " " + region);
	    			getCityToPrice(service, region, data_input, language, ts);
	    		}
	    	}
    	}
    	driver.close();

    }
    
    public static void getCityToPrice(String service, String region, 
    		String data_input, String language, long ts) throws IOException, InterruptedException {
    	
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
    	
    	Document d_=null;
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
    			try{
    				d_ = Jsoup.connect(zeroUrl).timeout(0).get();
    			}
    			catch(org.jsoup.HttpStatusException g) {
    				logger.info(g.toString());
    				//System.out.println("HTTP error fetching URL. Status=525");
    			}
    		}
    	}
    	if (d_ == null) return;
    	
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
    	//System.out.println(locsUrl);
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
    	for (Element link : links) {
    		String check = baseUrl+link.attr("href");
    		//System.out.println(check);
    		if (check.contains("/online/classifieds/PostAdPPI.html/?serverName="+region+".backpage.com&superRegion=") && !check.toLowerCase().contains("superRegion="+region) && !check.contains("?region=")) {
    			//System.out.println("YES");
    			nextUrls.add(check);// = check;
    			//break;
    		}
    	}
    	
    	for (String nextUrl : nextUrls) {
    		scrape(region, service, nextUrl, data_continue, language, url, baseUrl, data_login, false, ts);
    	}
		
    	if (nextUrls.size()==0) {
    		//handle the case where only one location
    		scrape(region, service, locsUrl, data_continue, language, url, baseUrl, data_login, true, ts);
    		
    	}
    	
    }
    
   public static void scrape(String region, String service, String nextUrl, String data_continue, 
		   String language, String url, String baseUrl, String data_login, Boolean alone, long ts) throws InterruptedException, IOException {
	   String chunk = "http://posting."+region+".backpage.com/online/classifieds/PostAdPPI.html"
				+ "/?serverName="+region+".backpage.com&superRegion=";
		int pos = nextUrl.indexOf(chunk) + chunk.length();
		int pos2 = nextUrl.indexOf("&", pos);
		String name = nextUrl.substring(pos, pos2).replace("%20", " ");
		if (alone) name = region;
		logger.info(name);
		//System.out.println(nextUrl);
		
		/*if (done.contains(name+service)) {
			System.out.println("already done");
			continue;
		}
		else done.add(name+service);*/
	
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
				logger.info("sorry! failed to find submit button");
			}
			catch (org.openqa.selenium.ElementNotVisibleException e2) {
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
				logger.info("sorry! failed to find submit button");
			}
			catch (org.openqa.selenium.ElementNotVisibleException e2) {
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
			logger.info("sorry! failed to find submit button");
		}
		catch (org.openqa.selenium.ElementNotVisibleException e2) {
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
		logger.info("no login found");
	}
	
	//Thread.sleep(5000);
	
	String html = driver.getPageSource();
	//Document parsed_html = Jsoup.parse(html);
	
	if (!html.equals("")) {
   	File file = new File("final_scrape/USA_"+ts+"_ESCORT/"
   	+region+"/"+service.replace("/", "")+"/"+name+"_"+System.currentTimeMillis()+".txt");
   	file.createNewFile();
   	FileWriter fileWriter = new FileWriter(file);
   	fileWriter.write(html);
   	fileWriter.flush();
   	fileWriter.close();
	}
   }
    
   public static Pair<ArrayList<String>,String> getServices(String language) {

	   ArrayList<String> services = new ArrayList<String>();
	   String data_name = "";
	   if (language == "us_edit") {
		   services.add("adult jobs");
     		services.add("body rubs");
     		services.add("domination & fetish");
     		services.add("male escorts");
     		services.add("escorts");
     		services.add("phone & websites");
     		services.add("strippers/strip clubs");
     		services.add("transsexual escorts");
		   data_name = "adult entertainment|Continue|Login";
		   }
	   else if (language == "english") {
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
	   else if (language == "czech") {
       		services.add("práce pro dospělé");
       		services.add("masáže & mazlení");
       		services.add("dominace & fetiš");
       		services.add("escort & privát");
       		services.add("pánský escort");
       		services.add("erotické linky & weby");
       		services.add("striptérky/strip clubs");
       		services.add("escort transsexuálů");
		   data_name = "erotika|Pokračovat|Přihlásit se";
		   }
	   else if (language == "danish") {
      		services.add("voksenjob");
      		services.add("kropsmassage");
      		services.add("dominans og fetich");
      		services.add("escortpiger");
      		services.add("escortfyre");
      		services.add("telefon og websteder");
      		//services.add("striptérky/strip clubs");
      		services.add("transseksuelle escort");
		   data_name = "voksenunderholdning|Fortsæt|Log in";
		   }
	   else if (language == "dutch") {
     		services.add("erotische vacatures");
     		services.add("body rubs & massage");
     		services.add("BDSM & fetish");
     		services.add("escorts");
     		services.add("mannelijke escorts");
     		services.add("telefoon & webcamsex");
     		//services.add("striptérky/strip clubs");
     		services.add("transseksuele escorts");
		   data_name = "erotiek|Doorgaan|Inloggen";
		   }
	   else if (language == "french") {
    		services.add("emplois pour adultes");
    		services.add("massages");
    		services.add("BDSM");
    		services.add("escortes");
    		services.add("gigolos");
    		services.add("téléphone - web");
    		//services.add("striptérky/strip clubs");
    		services.add("trans");
		   data_name = "adultes|Continuer|S'identifier";
		   }
	   else if (language == "german") {
   		services.add("Erotik Jobs");
   		services.add("Erotische Massagen");
   		services.add("BDSM, Bondage und Fetisch");
   		services.add("Escort");
   		services.add("Männliche Escorts");
   		services.add("Telefonsex");
   		//services.add("striptérky/strip clubs");
   		services.add("Shemale & Transsexuelle Escorts");
		data_name = "Erotik|Weiter|Login";
	   }
	   else if (language == "greek") {
	   		services.add("εργασία ενηλίκων");
	   		services.add("εντριβές σώματος");
	   		services.add("κυριαρχία & φετίχ");
	   		services.add("συνοδοί");
	   		services.add("άντρες συνοδοί");
	   		services.add("τηλέφωνα & ιστοσελίδες");
	   		//services.add("striptérky/strip clubs");
	   		services.add("τρανσέξουαλ συνοδοί");
			data_name = "διασκέδαση για ενηλίκους|Συνέχεια|Σύνδεση";
		}
	   else if (language == "hungarian") {
	   		services.add("felnőtt állások");
	   		services.add("body rub");
	   		services.add("domináció & fétis");
	   		services.add("escortok");
	   		services.add("férfi escortok");
	   		services.add("telefon & honlapok");
	   		//services.add("striptérky/strip clubs");
	   		services.add("transszexuális escortok");
			data_name = "felnőtt szórakoztatás|Tovább|Belépés";
		}
	   else if (language == "italian") {
	   		services.add("offerte di lavoro per adulti");
	   		services.add("massaggi erotici");
	   		services.add("dominazione e fetish");
	   		services.add("escort");
	   		services.add("accompagnatori");
	   		services.add("linee telefoniche e siti web");
	   		//services.add("striptérky/strip clubs");
	   		services.add("escort transessuali");
			data_name = "intrattenimento per adulti|Continua|Accedi";
		}
	   else if (language == "norweigan") {
	   		services.add("voksenjobber");
	   		services.add("kroppsmassasje");
	   		services.add("dominans & fetish");
	   		services.add("eskorte");
	   		services.add("mannlige eskorter");
	   		services.add("tel & nettsteder");
	   		//services.add("striptérky/strip clubs");
	   		services.add("transseksuell eskorte");
			data_name = "voksenunderholdning|Fortsett|Logg Inn";
		}
	   else if (language == "polish") {
	   		services.add("praca dla dorosłych");
	   		services.add("masaż erotyczny");
	   		services.add("dominacja & fetysz");
	   		services.add("escort");
	   		services.add("panowie do towarzystwa");
	   		services.add("randki i sex-telefony");
	   		//services.add("striptérky/strip clubs");
	   		services.add("transsexualiści do towarzystwa");
			data_name = "rozrywka dla dorosłych|Kontynuuj|Login";
		}
	   else if (language == "portuguese") {
	   		services.add("empregos adultos");
	   		services.add("massagens corporais");
	   		services.add("BDSM e fetiche");
	   		services.add("acompanhantes");
	   		services.add("acompanhantes masculinos");
	   		services.add("telefones & websites");
	   		//services.add("striptérky/strip clubs");
	   		services.add("travesti & transex");
			data_name = "adulto|Continuar|Entrar";
		}
	   else if (language == "russian") {
	   		services.add("интим работа");
	   		services.add("массаж");
	   		services.add("садо-мазо");
	   		services.add("индивидуалки");
	   		services.add("мужчины");
	   		services.add("вирт секс");
	   		//services.add("striptérky/strip clubs");
	   		services.add("транссексуалы");
			data_name = "развлечение для взрослых|Продолжить|Войти";
		}
	   else if (language == "spanish") {
	   		services.add("empleos eróticos");
	   		services.add("masajes eróticos");
	   		services.add("BDSM");
	   		services.add("escorts mujeres");
	   		services.add("escorts hombres");
	   		services.add("líneas eróticas");
	   		services.add("stripers");
	   		services.add("trans escorts");
	   		services.add("escorts trans");
	   		services.add("teléfonos - sitios");
			data_name = "eróticos|Publicar|Iniciar sesión";
		}
	   else if (language == "mexico") {
	   		services.add("empleos eróticos");
	   		services.add("masajes eróticos");
	   		services.add("BDSM");
	   		services.add("escorts mujeres");
	   		services.add("escorts hombres");
	   		services.add("líneas eroticas");
	   		services.add("stripers");
	   		services.add("escorts trans");
			data_name = "eróticos|Publicar|Iniciar sesión";
		}
	   else if (language == "turkish") {
	   		services.add("yetişkin işleri");
	   		services.add("özel masaj");
	   		services.add("dominant & fetiş");
	   		services.add("eskortlar");
	   		services.add("erkek eskortlar");
	   		services.add("telefon & web siteleri");
	   		//services.add("striptérky/strip clubs");
	   		services.add("transseksüel eskortlar");
			data_name = "yetişkin eğlencesi|Devam|Giriş yap";
		}	
	   return new Pair<ArrayList<String>, String>(services, data_name);
   }
}

