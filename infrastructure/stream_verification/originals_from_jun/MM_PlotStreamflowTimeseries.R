# This script will plot daily, weekly, and monthly streamflow at USGS
# stream gauges with simulated ParFlow CONUS flow. One figure is written 
# for every stream gauge. DownloadStreamflow.R and OrganizeStreamflow.R
# must have been run before running this script.
#
# Required scripts:
# - Must have run DownloadStreamflow.R and OrganizeStreamflow.R
#
# Required inputs:
# - Directory containing outputs from OrganizeStreamflow.R
# - Sequence of water years you want included in the plot.
# - Output directory for individual gauge figures.
# - Path to station information csv
#
# Outputs:
# - ID#_FlowMatch_Timeseries.pdf for each USGS stream gauge, which contains three
#   subplots: daily, weekly, and monthly aggregates of USGS (black) and ParFlow (red)
#   timeseries, along with performance metrics (R2, Spearman, RMSE, etc.) and a
#   summary of important station characteristics.

# Note to self - need to go back and change sRMSE (RMSE scaled by range) to RSR
# (RMSE scaled by standard deviation)

# Required libraries
library(xts) # Date time package, helpful for weekly/monthly/annual aggregates
library(hydroGOF) # Helps with error statistics

#######################################
# Script inputs

# Where are the results of OrganizeStreamflow.R?
organized_dir = "./Organized_Daily_Flow/"

# Which water years do you want to compare?
WYs = 2003:2005

# Output directory for gauge figures
outdir = "./Gauge_Timeseries_Comparisons/"

# Summary file of station information
# This is the summary of PF performance at gauges from the 1985 CONUS 1.0 version
stat_info = "./COMBINED_MASTER_AllStations_Summary.csv"

# Read in and combine daily tables - these are outputs from OrganizeStreamflow.R
# I need to go back and change this to just do the whole timeseries at once
# instead of splitting it up by water year
pfdata = as.matrix(read.csv(paste(organized_dir,
                                  "CONUS_GaugesFlowMatch_daily_WY",
                                  WYs[1],".csv",sep="")))
udata = as.matrix(read.csv(paste(organized_dir,
                                 "USGS_GaugesFlowMatch_daily_WY",
                                 WYs[1],".csv",sep="")))

for(i in 2:length(WYs)){
  
  hold_pf = as.matrix(read.csv(paste(organized_dir,
                                     "CONUS_GaugesFlowMatch_daily_WY",
                                     WYs[i],".csv",sep="")))
  hold_usgs = as.matrix(read.csv(paste(organized_dir,
                                       "USGS_GaugesFlowMatch_daily_WY",
                                       WYs[i],".csv",sep="")))
  
  pfdata = cbind(pfdata,hold_pf)
  udata = cbind(udata,hold_usgs)
  
}

#######################################
# Timeframe, station info

# Timeframe
start = as.Date(paste(WYs[1]-1,"-10-01",sep=""))
end = as.Date(paste(WYs[length(WYs)],"-09-30",sep=""))
dates = as.Date(start:end)
dates_mon = seq(as.Date(start),as.Date(end),length=12)

# Station information
station_info=read.csv(stat_info, header=T) 
nstat = nrow(station_info)

#######################################
# Loop through gauges
# 1. Create daily, weekly, monthly xts objects
# 2. Calculate some performance stats
# 3. Make figure and print

for(i in 1:nstat){ # Loop through stations
 
  # Check to make sure observation record is not empty-
  # We need at least 3 observations
  # if it is emty, then skip to next gauge
  if(length(which(!is.na(udata[i,]))) < 3){
      print("WARNING: No data in observation record!")
      next
  }
 
  # 1. XTS OBJECTS AND TEMPORAL AGGREGATES 
  
  # Daily xts object at gauge
  obs_xts = xts(udata[i,],dates)
  sim_xts = xts(pfdata[i,],dates)
  
  # Weekly aggregates
  # We are taking the mean in case there are missing data during a single week
  obs_week = apply.weekly(obs_xts,FUN=mean,na.rm=T) 
  sim_week = apply.weekly(sim_xts,FUN=mean,na.rm=T)
  
  # Monthly aggregates
  obs_mon = apply.monthly(obs_xts,FUN=mean,na.rm=T)
  sim_mon = apply.monthly(sim_xts,FUN=mean,na.rm=T)
  
  # 2. PERFORMANCE METRICS 
  # Just a note - percent bias should not change significantly between aggregation periods
  
  # Daily
  r_daily = cor.test(as.numeric(obs_xts),as.numeric(sim_xts))$estimate^2
  rho_daily = cor.test(as.numeric(obs_xts),as.numeric(sim_xts),method='spearman')$estimate
  RMSE_daily = rmse(as.numeric(sim_xts),as.numeric(obs_xts),na.rm=T)
  pb_daily = pbias(as.numeric(sim_xts),as.numeric(obs_xts),na.rm=T)
  sRMSE_daily = RMSE_daily/(max(obs_xts,na.rm=T) - min(obs_xts,na.rm=T))
  # Weekly
  r_weekly = cor.test(as.numeric(obs_week),as.numeric(sim_week))$estimate^2
  rho_weekly = cor.test(as.numeric(obs_week),as.numeric(sim_week),method='spearman')$estimate
  RMSE_weekly = rmse(as.numeric(sim_week),as.numeric(obs_week),na.rm=T)
  pb_weekly = pbias(as.numeric(sim_week),as.numeric(obs_week),na.rm=T)
  sRMSE_weekly = RMSE_weekly/(max(obs_week,na.rm=T) - min(obs_week,na.rm=T))
  # Monthly
  r_monthly = cor.test(as.numeric(obs_mon),as.numeric(sim_mon))$estimate^2
  rho_monthly = cor.test(as.numeric(obs_mon),as.numeric(sim_mon),method='spearman')$estimate
  RMSE_monthly = rmse(as.numeric(sim_mon),as.numeric(obs_mon),na.rm=T)
  pb_monthly = pbias(as.numeric(sim_mon),as.numeric(obs_mon),na.rm=T)
  sRMSE_monthly = RMSE_monthly/(max(obs_mon,na.rm=T) - min(obs_mon,na.rm=T))
  # Total
  # NOTE: The pbias function in hydroGOF removes observed AND simulated data if either are missing
  # So bias statistics do not include missing data... should we report mean annual flow with or without
  # missing observations? So if we have two years of USGS data and three of ParFlow, should all of
  # ParFlow be reported or just the missing data?
  # Here I'm choosing to use all available PF data when reporting Annual Mean Flow, but removing
  # dates where observations are missing when reporting any type of bias.
  relbias = pb_daily/100
  bias = relbias*mean(as.numeric(obs_xts),na.rm=T)*365*24*3600 # In cubic meters per year 
  pf_tot = mean(as.numeric(sim_xts * (24*3600)),na.rm=T)*365 # In cubic meters per year
  usgs_tot = mean(as.numeric(obs_xts * (24*3600)),na.rm=T)*365 # In cubic meters per year
  #bias = pf_tot - usgs_tot
  #relbias = (pf_tot - usgs_tot)/usgs_tot
  
  # 3. SET UP FIGURE
  png(paste(outdir,station_info$STAID[i],"_monthly_comparisons.png",sep=""),
      height=3000,width=3000,res=400)
  layout(mat = matrix(c(1,1,1,
                        2,2,2,
                        3,3,3,
                        4,5,6),
                      nrow=4,
                      ncol=3,
                      byrow=T))
  par(mar=c(1,4,2,1))
  
  # 4. PLOT TIMESERIES
  # Daily
  plot(index(obs_xts),as.numeric(obs_xts),
       main=station_info$STANAME[i],
       type='l',
       xlab="",ylab="Daily discharge (cms)",
       yaxt='n',xaxt='n',
       lwd=2,
       xlim=c(start,end),
       ylim=c(min(c(as.numeric(obs_xts),as.numeric(sim_xts)),na.rm=T),
              max(c(as.numeric(obs_xts),as.numeric(sim_xts)),na.rm=T)))
  lines(index(sim_xts),as.numeric(sim_xts),col='coral2',lwd=2)
  axis(2,las=2)
  axis(1,at=seq(as.Date(start),as.Date(end),by='years'),labels=NA)
  legend('topright',legend=c("USGS Gauge","CONUS PFCLM"),
         lty=1,lwd=2,
         col=c("black","coral2"))
  
  # Weekly 
  plot(index(obs_week),as.numeric(obs_week),
       type='l',
       xlab="",ylab="Mean weekly discharge (cms)",
       yaxt='n',xaxt='n',
       lwd=2,
       xlim=c(start,end),
       ylim=c(min(c(as.numeric(obs_week),as.numeric(sim_week)),na.rm=T),
              max(c(as.numeric(obs_week),as.numeric(sim_week)),na.rm=T)))
  lines(index(sim_week),as.numeric(sim_week),col='coral2',lwd=2)
  axis(2,las=2)
  axis(1,at=seq(as.Date(start),as.Date(end),by='years'),labels=NA)
  
  # Monthly
  plot(index(obs_mon),as.numeric(obs_mon),
       type='l',
       xlab="",ylab="Mean monthly discharge (cms)",
       yaxt='n',xaxt='n',
       lwd=2,
       xlim=c(start,end),
       ylim=c(min(c(as.numeric(obs_mon),as.numeric(sim_mon)),na.rm=T),
              max(c(as.numeric(obs_mon),as.numeric(sim_mon)),na.rm=T)))
  lines(index(sim_mon),as.numeric(sim_mon),col='coral2',lwd=2)
  axis(2,las=2)
  axis(1,at=seq(as.Date(start),as.Date(end),by='years'),
       labels = as.Date(seq(as.Date(start),as.Date(end),by='years')))
  
  # 5. STATION INFORMATION
  
  # Development information  
  par(mar=c(0,0,2,0))
  plot.new()
  legend('topleft', legend=c("Development",
                             paste("Disturbance Index:", station_info$DIST_INDX[i]),
                             paste("Number of Dams 1990:", station_info$X1990_NDAM[i]),
                             paste("Dam Storage 1990 (1000 m³):", round(station_info$X1990_STOR[i]*station_info$DRAIN_SQKM[i],1)),
                             paste("Distance to nearest dam (km):", station_info$DIS_DAM[i]),
                             paste("Withrawals 95-00 (1000 m³ per yr):",station_info$FRWA_WDRL[i]*station_info$DRAIN_SQKM[i]),
                             paste("Portion of Watershed Irrigated in 2002: ",station_info$PCT_IRRIG[i], "%", sep="")
                             
  ),text.font=c(2,1,1,1,1,1,1),bty="n", cex=0.9)
  
  # Drainage area differences
  plot.new()
  legend('topleft', legend=c("Drainage Area",
                          paste("Gages:" , station_info$DRAIN_SQKM[i], "km²"),
                          paste("NWIS:", station_info$NWIS_DRAIN[i], "km²"),
                          paste("ParFlow:", round(station_info$PF_Area[i],1), "km²"),
                          paste("Diff PF vs Gages: ", round((station_info$PF_Area[i]-station_info$DRAIN_SQKM[i])/station_info$DRAIN_SQKM[i]*100,1), "%", sep=""),
                          "",
                          
                          "Annual Flow Volume",
                          paste("ParFLow:" , round(pf_tot/10^6,2), "MCM per year"),
                          paste("USGS Gage:", round(usgs_tot/10^6,2), "MCM per year"),
                          paste("Bias:", round(bias/10^6,2), "MCM per year"),
                          paste("Relative Bias: ",round(relbias,3)*100,"%",sep="")

                          
  ),text.font=c(2,1,1,1,1,1,2,1,1,1,1),bty="n", cex=0.9)
  
  # 6. WRITE PERFORMANCE STATISTICS
  
  # Drainage area differences
  plot.new()
  legend('topleft', legend=c("Correlation",
                             paste("Daily Spearman rho:",round(rho_daily,2)),
                             paste("Weekly Spearman rho:",round(rho_weekly,2)),
                             paste("Monthly Spearman rho:",round(rho_monthly,2)),
                             paste("Daily R²:",round(r_daily,2)),
                             paste("Weekly R²:",round(r_weekly,2)),
                             paste("Monthly R²:",round(r_monthly,2)),
                             
                             "",
                             "Monthly RMSE",
                             paste("RMSE:",round(RMSE_monthly,2)),
                             paste("Range-scaled RMSE: ",round(sRMSE_monthly*100,1),"%",sep="")

  ),text.font=c(2,1,1,1,1,1,1,1,2,1,1),bty="n", cex=0.9)
  
  
  
  dev.off()
 

  # Tracking script progress
  print(i) 
  
} # End loop through stations


