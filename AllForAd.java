package backpages;

import java.util.*;

public class AllForAd {

	private int ID;
	private String text;
	private ArrayList<String> locations;
	private PriorityQueue<Timestamp> times;
	private boolean complete;
	private String category;
	private boolean sponsor;
	private int firstsponsor;
	private int lastsponsor;

	public AllForAd(String scrape){
		this.locations = new ArrayList<String>();
		this.times = new PriorityQueue<Timestamp>();
		this.complete = true;
		this.sponsor = false;
		this.firstsponsor = Integer.MAX_VALUE;
		this.lastsponsor = 0;
		if(scrape.contains("no date object")){
			//System.out.println("no date object");
			this.complete = false;
		}
		if(scrape.contains("failed to get")){
			//System.out.println("failed to get");
			this.complete = false;
		}
		if(scrape.contains("date object empty")){
			//System.out.println("date object empty");
			this.complete = false;
		}
		if(scrape.contains("fail")){
			//System.out.println("fail");
			this.complete = false;
		}

		String[] bits = scrape.split("\\) ");
		String[] locs = {};
		//no locations to remove
		if(bits.length == 1){
			String[] getlocs = scrape.split(":00  ");
			String[] getlocs1 = getlocs[getlocs.length-1].split(", ");
			locs = getlocs1;
		}
		else{
			//System.out.println(bits[bits.length-1]);
			locs = bits[bits.length-1].split(", ");
		}
		bits = scrape.split("/");
		this.category = bits[3];
		String[] bits1 = bits[5].split(" ");
		this.ID = Integer.parseInt(bits1[0]);

		if(this.complete){
			locationMap lm = new locationMap();

			String date = bits1[1];
			String time = bits1[2];
			if(locs.length == 0){
				for(int i = 3; i<bits1.length; i++){
					String [] tmp = bits1[i].split(",");
					String [] tmp2 = tmp[0].split(" ");
					String toadd = "";
					if(tmp2.length == 1){
						toadd = tmp2[0];
					}else{
						toadd = tmp2[1];
					}
					//System.out.println(toadd);
					if(lm.realPlace(toadd.toLowerCase())){
						this.locations.add(toadd.toLowerCase());
					}
				}
			}else{
				for(int i = 0; i<locs.length; i++){
					//System.out.println(locs[i]);

					if(lm.realPlace(locs[i].toLowerCase())){
						if(!(this.locations.contains(locs[i].toLowerCase()))){
							this.locations.add(locs[i].toLowerCase());
						}
					}
				}
			}
			if(this.locations.size() == 0){
				this.complete = false;
			}else{
				String[] getdate = date.split("-");
				String[] gettime = time.split(":");
				Timestamp t = new Timestamp(Integer.parseInt(getdate[0]), Integer.parseInt(getdate[1]), Integer.parseInt(getdate[2]), Integer.parseInt(gettime[0]), Integer.parseInt(gettime[1]), this.locations);
				times.add(t);
			}
			//parse date and time to create timestamp

		}else{
			System.out.println("incomplete: "+scrape);

		}
	}

	public void update(String scrape){
		locationMap lm = new locationMap();
		if(scrape.contains("no date object")){
			this.complete = false;
		}
		if(scrape.contains("failed to get")){
			this.complete = false;
		}
		if(scrape.contains("date object empty")){
			this.complete = false;
		}
		if(scrape.contains("fail")){
			this.complete = false;
		}
		String[] bits = scrape.split("\\)");
		String[] locs = {};
		//no locations to remove
		if(bits.length == 1){

		}
		else{
			locs = bits[bits.length-1].split(", ");
		}
		bits = scrape.split("/");
		this.category = bits[3];
		String[] bits1 = bits[5].split(" ");
		this.ID = Integer.parseInt(bits1[0]);

		if(this.complete){
			String date = bits1[1];
			String time = bits1[2];
			if(locs.length == 0){
				for(int i = 3; i<bits1.length; i++){
					String [] tmp = bits1[i].split(",");
					if(lm.realPlace(tmp[0].toLowerCase())){
						if(!this.locations.contains(tmp[0].toLowerCase())){
							this.locations.add(tmp[0].toLowerCase());
						}
					}
				}
			}else{
				for(int i = 0; i<locs.length; i++){
					if(lm.realPlace(locs[i].toLowerCase())){
						if(!this.locations.contains(locs[i].toLowerCase())){
							this.locations.add(locs[i].toLowerCase());
						}
					}
				}
			}
			//parse date and time to create timestamp
			String[] getdate = date.split("-");
			String[] gettime = time.split(":");
			Timestamp t = new Timestamp(Integer.parseInt(getdate[0]), Integer.parseInt(getdate[1]), Integer.parseInt(getdate[2]), Integer.parseInt(gettime[0]), Integer.parseInt(gettime[1]), this.locations);
			this.times.add(t);
		}
		//System.out.println(this.ID+" updated. Now has "+this.times.size()+" timestamps.");
	}

	public boolean isComplete(){
		return this.complete;
	}

	public boolean sponsorUpdate(int timestamp){
		if(this.sponsor == false){
			this.sponsor = true;
			if(timestamp > lastsponsor){
				lastsponsor = timestamp;
			}
			if(timestamp < firstsponsor){
				firstsponsor = timestamp;
			}
			return true;
		}
		//System.out.println(this.ID+" has "+this.times.size()+" timestamps and was sponsored");
		this.sponsor = true;
		if(timestamp > lastsponsor){
			lastsponsor = timestamp;
		}
		if(timestamp < firstsponsor){
			firstsponsor = timestamp;
		}
		return false;
	}

	public int[] getSponsorTimes(){
		int[] times = {this.firstsponsor, this.lastsponsor};
		return times;
	}

	public PriorityQueue<Timestamp> getTimes(){
		return this.times;
	}

	public int getID(){
		return this.ID;
	}

	public String getCategory(){
		return this.category;
	}

	public ArrayList<String> getLocs(){
		return this.locations;
	}

	public boolean isSponsored(){
		return this.sponsor;
	}
}
