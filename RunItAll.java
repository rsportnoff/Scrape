package backpages;
import java.util.*;
import java.io.*;

public class RunItAll {

	public static void main(String[] args){

		ArrayList<PriceSet> priceMap = new ArrayList<PriceSet>();
		File p = new File("all_pricing");
		File[] ps = p.listFiles();
		for(int i = 1; i<ps.length; i++){
			System.out.println("folder: "+ps[i].getName());
			File[] ls = ps[i].listFiles();
			for(int j = 1; j<ls.length; j++){
				System.out.println("location: "+ls[j].getName());
				if(ls[j].getName().contains("log")){
					//skip
				}else{
					File[] cats = ls[j].listFiles();
					for(int k = 1; k<cats.length-2; k++){
						System.out.println("category: "+cats[k].getName());
						File[] prices = cats[k].listFiles();
						String cat = cats[k].getName();
						for(int l = 0; l<prices.length; l++){
							System.out.println("file: "+prices[l].getName());
							String[] tmp = prices[l].getName().split("_");
							String loc = tmp[0];
							String[] tmp2 = tmp[1].split("\\.");
							System.out.println(tmp2[0]);
							long time = Long.parseLong(tmp2[0]);
							try{
								BufferedReader f = new BufferedReader(new FileReader(prices[l]));
								String line; 
								while((line = f.readLine()) != null){
									if(line.contains("<input type=\"checkbox\" data")){
										System.out.println(line);
										String[] bits = line.split(" ");
										double bump = 0, rep =0, base=0, spon=0;
										for(int q = 0; q<bits.length; q++){
											String[] bits2 = bits[q].split("=");
											if(bits[q].contains("movetotopprice")){
												String[] bits3 = bits2[1].split("\"");
												bump = Double.parseDouble(bits3[1]);
											}
											if(bits[q].contains("sponsorprice")){
												String[] bits3 = bits2[1].split("\"");
												spon = Double.parseDouble(bits3[1]);
											}
											if(bits[q].contains("autorepostprice")){
												String[] bits3 = bits2[1].split("\"");
												rep = Double.parseDouble(bits3[1]);
											}
											if(bits[q].contains("baseprice")){
												String[] bits3 = bits2[1].split("\"");
												base = Double.parseDouble(bits3[1]);
											}
										}
										line = f.readLine();
										String[] gl = line.split(">");
										String[] gl2 = gl[1].split(" - ");
										String newloc = gl2[0];
										PriceSet set = new PriceSet(newloc, time, cat);
										set.setBase(base);
										set.setBump(bump);
										set.setRepost(rep);
										set.setSponsor(spon);
										if(!(priceMap.contains(set))){
											priceMap.add(set);

										}

									}
								}
								System.out.println(priceMap.size());
							}catch(IOException e){
								System.out.println("issue with price file: "+cat+" "+loc+" "+time);
							}
						}
					}
				}
			}
		}

		Collections.sort(priceMap);
		File adfiles = new File("files");
		File[] adlocs = adfiles.listFiles();

		File sponsor = new File("sponsor_ads");
		File[] sponsorlocs = sponsor.listFiles();

		System.out.println(adlocs.length);
		System.out.println(sponsorlocs.length);


		//for each location category
		for(int i = 22; i<adlocs.length; i++){
			File tmpad = adlocs[i];
			File tmpspon = sponsorlocs[i];
			System.out.println(tmpad.getName());
			System.out.println(tmpspon.getName());
			HashMap<Integer, AllForAd> ads = new HashMap<Integer, AllForAd>();
			int sponsored = 0;
			try{
				//regular ads
				BufferedReader adreader = new BufferedReader(new FileReader(tmpad));
				//multiple files for the sponspor ads

				String ad;
				while((ad = adreader.readLine()) != null){
					if(ad.startsWith("http")){
						String[] bits = ad.split("/");
						String[] bits2 = bits[5].split(" ");
						String adid = bits2[0];
						int id = Integer.parseInt(adid);
						//new id
						if(!ads.containsKey(id)){
							//System.out.println("new ad: "+id);
							AllForAd tmp = new AllForAd(ad);
							ads.put(id, tmp);
						}
						//not a new id
						else{
							//System.out.println("updating: "+id);
							AllForAd tmp = ads.get(id);
							//ignore if incomplete
							if(tmp.isComplete()){
								tmp.update(ad);

							}
						}
					}

				}
				System.out.println(ads.size());
			}catch(IOException e){
				e.printStackTrace();
				System.out.println("problem opening ad file");
			}

			try{
				File[] times = tmpspon.listFiles();
				System.out.println("checking sponsor files: ");
				for(int i1 = 1; i1<times.length; i1++){
					File f = times[i1];
					String time = f.getName();
					System.out.println(time);
					File[] categories = f.listFiles();
					for(File c:categories){
						BufferedReader br = new BufferedReader(new FileReader(c));
						String line;
						while((line = br.readLine()) != null){
							if(line.contains("sponsorBoxContent")){
								String[] parts = line.split("><");
								String[] parts2 = parts[2].split("/");
								String[] getID = parts2[5].split("\">");
								int ID = Integer.parseInt(getID[0]);
								if(ads.containsKey(ID)){
									AllForAd tmp = ads.get(ID);
									boolean temp = tmp.sponsorUpdate(Integer.parseInt(time));
									if(temp){
										sponsored++;
									}
								}
							}
						}

					}
				}
			}catch(IOException e){
				System.out.println("problem opening sponsor file");
			}

			System.out.println("total ads: "+ads.size()+" sponsored ads: "+sponsored);

			try{
				String  filename = "preliminary_output_"+tmpad.getName();
				File postfile = new File(filename);
				FileWriter post = new FileWriter(postfile);

				Collection<AllForAd> list = ads.values();
				Iterator<AllForAd> it = list.iterator();
				for(int x = 0; x<list.size(); x++){
					System.out.println("ad number: "+x);
					AllForAd a = it.next();
					if(a.isComplete()){
						PriorityQueue<Timestamp> times = a.getTimes();

						post.write("\n\n"+a.getID()+", "+times.peek().getUnix()+", "+times.peek().toString()+", "+a.getCategory());

						Timestamp currtime = times.poll();
						PriceSet[] prices = new PriceSet[a.getLocs().size()];
						post.write("\nposted in: ");
						for(int y = 0; y<a.getLocs().size(); y++){
							PriceSet tmp = new PriceSet(a.getLocs().get(y), currtime.getUnix(), a.getCategory());
							int y2 = 0;
							System.out.println(tmp.getCat()+" "+tmp.getLoc()); 
							while(tmp.compareTo(priceMap.get(y2)) > 0){
								//System.out.println(y2+" "+tmp.compareTo(priceMap.get(y2))+" "+priceMap.get(y2).getCat()+" "+priceMap.get(y2).getLoc());
								y2++;

							}
							System.out.println(y2+" "+priceMap.get(y2).getCat());
							prices[y] = priceMap.get(y2);
							post.write(a.getLocs().get(y)+", ");
						}
						boolean manual = false;
						int bumps = 0;
						int reposts = 0;
						int rephour = 0;
						double grandsum = 0;
						double sponsordays = 0;
						String transaction = "";
						if(a.isSponsored()){
							transaction += "\nsponsored from: "+a.getSponsorTimes()[0]+" to: "+a.getSponsorTimes()[1];
							sponsordays = (double)(a.getSponsorTimes()[1] - a.getSponsorTimes()[0])/86400;
							double sum = 0;
							for(int s = 0; s<prices.length; s++){
								sum += prices[s].getSpon();
							}
							sum *= Math.ceil(sponsordays/7.0);
							transaction += "\ntotal sponsor cost: "+sum;
							grandsum += sum;
						}else{
							double sum = 0;
							for(int s = 0; s<prices.length; s++){
								sum += prices[s].getSpon();
							}
							transaction += "\nhypothetical sponsor cost, one week: "+sum;
						}
						post.write(transaction);
						while(!(times.isEmpty())){
							Timestamp nexttime = times.poll();

							if(currtime.getDay() == nexttime.getDay() - 1){
								if(currtime.getMilitaryHour() == 23 && nexttime.getMilitaryHour() == 0){
									bumps++;
								}
								else if(reposts == 0){
									reposts++;	
									rephour = nexttime.getMilitaryHour();
								}else{
									if(nexttime.getMilitaryHour() == rephour){
										reposts++;
									}else{
										manual = true;
									}
								}	
							}else if(currtime.getDay() == nexttime.getDay()){
								if(currtime.getMilitaryHour() == nexttime.getMilitaryHour()){
									if(currtime.getMinute() == nexttime.getMinute()){
										//same time - different locations - ignore
									}else{
										manual = true;
									}
								}
								else if(currtime.getMilitaryHour() == nexttime.getMilitaryHour()-1){
									if(currtime.getMinute() == nexttime.getMinute()){
										bumps++;
									}else{ //off by not exactly an hour
										manual = true;
									}
								}else{ //different hour altogether
									manual = true;
								}
							}else{
								manual = true;
							}

							if(manual){
								double sum = 0;
								if(prices.length > 1){
									for(int s = 0; s<prices.length; s++){
										sum += prices[s].getBase();
									}
								}
								post.write("\nmultiple location cost: "+sum);
								grandsum += sum;
								post.write("\nbumps: "+bumps+"\nreposts: "+reposts);
								///some calculations regarding price
								sum = 0;
								for(int s = 0; s<prices.length; s++){
									sum += prices[s].getBump();
								}
								sum *= bumps;
								grandsum += sum;
								post.write("\nbump cost: "+sum);
								sum = 0;
								for(int s = 0; s<prices.length; s++){
									sum += prices[s].getRep();
								}
								if(reposts >= 4){
									sum = (sum / 4)*reposts;
								}else{
									sum = 0;
								}
								grandsum += sum;
								post.write(", repost cost: "+sum);
								bumps = 0;
								reposts = 0;
								rephour = 0;
								manual = false;
								post.write("\ntotal cost for posting: "+grandsum);
								grandsum = 0;
								post.write("\nmanual repost: "+nexttime.toString()+" "+nexttime.getUnix());
								for(int y = 0; y<a.getLocs().size(); y++){
									PriceSet tmp = new PriceSet(a.getLocs().get(y), nexttime.getUnix(), a.getCategory());
									int y2 = 0;
									while(priceMap.get(y2).compareTo(tmp) < 0){
										y2++;
									}
									prices[y] = priceMap.get(y2);
								}
							}
							currtime = nexttime;
							manual = false;
						}
						double sum = 0;
						if(prices.length > 1){
							for(int s = 0; s<prices.length; s++){
								sum += prices[s].getBase();
							}
						}
						grandsum += sum;
						post.write("\nmultiple location cost: "+sum);
						post.write("\nbumps: "+bumps+"\nreposts: "+reposts);
						///some calculations regarding price
						sum = 0;
						for(int s = 0; s<prices.length; s++){
							sum += prices[s].getBump();
						}
						sum *= bumps;
						grandsum += sum;
						post.write("\nbump cost: "+sum);
						sum = 0;
						for(int s = 0; s<prices.length; s++){
							sum += prices[s].getRep();
						}
						if(reposts >= 4){
							sum = (sum / 4)*reposts;
						}else{
							sum = 0;
						}
						grandsum += sum;
						post.write(", repost cost: "+sum);
						post.write("\ntotal cost of posting: "+grandsum);
					}
					else{
						post.write("\n\n"+a.getID()+" data collection error");
					}
				}
			}
			catch(IOException e){
				System.out.println("issue writing file");
			}
		}




	}

}


