package backpages;


import java.util.ArrayList;
//holds a timestamp and a list of locations
public class Timestamp implements Comparable<Timestamp>{
	
	private Long unix;
	private ArrayList<String> loc; //assigned in constructor
	private int id; //assigned in constructor
	private String month; //assigned in constructor
	private int m;
	private int day; //assigned in constructor
	private int year; //in constructor
	private int hour; //in constructor
	private int minute; //in constructor
	private boolean am; //in constructor
	private int militaryHour;//in constructor
	
	//for use with the list of ads
	public Timestamp(String text){
		String[] bits = text.split("      ");
		this.id = Integer.parseInt(bits[0]);
		
		//time information
		String[] when = bits[1].split(",");
		String[] date = when[1].split(" ");
		//formatted _month_day
		if(date.length == 3){
			this.month = date[1];
			this.day = Integer.parseInt(date[2]);
			
			String[] temp = when[2].split("'");
			String[] time = temp[0].split(" ");
			
			this.year = Integer.parseInt(time[1]);
			
			String ampm = time[3];
			if(ampm.equals("AM")){
				this.am = true;
			}else{
				this.am = false;
			}
			
			String[] hm = time[2].split(":");
			this.hour = Integer.parseInt(hm[0]);
			this.minute = Integer.parseInt(hm[1]);
		}
		//formatted _day_month_year
		else if(date.length == 4){
			this.month = date[2];
			this.day = Integer.parseInt(date[1]);
			this.year = Integer.parseInt(date[3]);
			
			String[] temp = when[2].split("'");
			String[] time = temp[0].split(" ");
			String[] hm = time[1].split(":");
			
			//in 12 hour time
			if(time.length == 3){
				//am or pm
				String ampm = time[2];
				if(ampm.equals("AM")){
					this.am = true;
				}else{
					this.am = false;
				}
				this.hour = Integer.parseInt(hm[0]);
				this.minute = Integer.parseInt(hm[1]);
				//calculate military hour
				if(this.am){
					if(this.hour == 12){
						this.militaryHour = 0;
					}else{
						this.militaryHour = this.hour;
					}
				}else{
					if(this.hour == 12){
						this.militaryHour = this.hour;
					}else{
						this.militaryHour = this.hour +12;
					}
				}
				
			}
			//already in 24 hour time
			else if(time.length == 2){
				this.militaryHour = Integer.parseInt(hm[0]);
				this.minute = Integer.parseInt(hm[1]);
			}
			
			
		}
		
		
		String[] place1 = bits[2].split("'");
		//first set of locations
		String[] place3 = place1[1].split(",");
		//second set of locations
		String[] place2 = bits[3].split("'");
		
		this.loc = new ArrayList<String>();
		for(int i =1; i<place2.length-1;i++){
			loc.add(place2[i]);
		}
		for(int j = 0; j<place3.length; j++){
			if(j >0){
				String[] tmp = place3[j].split(" ", 2);
				
				if(tmp.length == 1){
					this.loc.add(tmp[0]);
				}else{
					this.loc.add(tmp[1]);
				}
			}else{
				this.loc.add(place3[j]);
			}
		}
		
		
	}
	//for use with the scraped ads
	public Timestamp(int year, int month, int day, int militaryHour, int minute, ArrayList<String> locs){
		this.year = year;
		this.m = month;
		this.day = day;
		this.militaryHour = militaryHour;
		this.minute = minute;
		this.loc = locs;
		Time_to_UNIX.func(this);
	}
	
	public ArrayList<String> getLoc(){
		return this.loc;
	}
	
	
	
	public int getDay(){
		return this.day;
	}
	
	public long getUnix(){
		return this.unix;
	}
	
	public int getYear(){
		return this.year;
	}

	public int getMilitaryHour(){
		return this.militaryHour;
	}
	
	public int getMinute(){
		return this.minute;
	}
	public int getID(){
		return this.id;
	}
	public int getMonth(){
		if(this.m != 0){
			return this.m;
		}
		String m = this.month.toLowerCase();
		if(m.equals("january")){
			return 1;
		}if(m.equals("february")){
			return 2;
		}if(m.equals("march")){
			return 3;
		}if(m.equals("april")){
			return 4;
		}if(m.equals("may")){
			return 5;
		}if(m.equals("june")){
			return 6;
		}if(m.equals("july")){
			return 7;
		}if(m.equals("august")){
			return 8;
		}if(m.equals("september")){
			return 9;
		}if(m.equals("october")){
			return 10;
		}if(m.equals("november")){
			return 11;
		}if(m.equals("december")){
			return 12;
		}
		return 0;
	}
	
	public void setUnix(long unix){
		this.unix = unix;
		//System.out.println("unix is set to: "+unix);
	}
	@Override
	public int compareTo(Timestamp o) {
		if(o.unix != 0 && this.unix != 0){
			return this.unix.compareTo(o.unix);
		}else{
			int sum = 0;
			sum += this.year-o.year;
			if(sum != 0){
				return sum;
			}
			sum += this.m - o.m;
			if(sum != 0){
				return sum;
			}
			sum += this.day - o.day;
			if(sum != 0){
				return sum;
			}
			sum += this.militaryHour - o.militaryHour;
			if(sum != 0){
				return sum;
			}
			sum += this.minute - o.minute;
			return sum;
		}
	}
	
	public String toString(){
		String t =  this.m+"-"+this.day+"-"+this.year+","+this.militaryHour+":";
		if(this.minute < 10){
			t += "0";
		}
		t += this.minute;
		return t;
	}
	
}
