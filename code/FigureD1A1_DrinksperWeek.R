library("fixest")
library("tidyverse")
# library("hrbrthemes")
library("ggpubr")
library("patchwork")
library("MetricsWeighted")
library("arrow")

# Read in the parquet for 2018
fn_in <- "~/Dropbox/sin_tax_project/proc_data/cluster_data_all_years.parquet"

# Outputs
fn_drinks <- "~/Dropbox/sin_tax_project/figures/FigureA1.pdf"
fn_log_level <- "~/Dropbox/sin_tax_project/figures/FigureD1.pdf"

p = c(0.5,0.75,0.9,0.95,0.99)
# dplyr/purrr/rlang solution 
get_percentiles<-function(df2,var){
  part1<- df2 %>%
    group_by(median_income) %>%
    summarize(value = weighted_quantile(!! sym(var), w = projection_factor, probs =p, na.rm = TRUE),.groups = 'drop') %>%
    
    mutate(p_tiles = rep(paste0(p*100, "%"),13)) %>%
    pivot_wider(names_from=p_tiles, values_from=value)
  
  part2<- df2 %>% 
    group_by(median_income) %>%
    summarize(avg = weighted.mean(!! sym(var),w = projection_factor),
              avg_log =exp(weighted_mean(log(1+!! sym(var)),w = projection_factor)),
              stdev=sqrt(weighted_var(!! sym(var),w = projection_factor)),
              .groups = 'drop')
  
  inner_join(part1,part2)
}

make_long <- function(df2){
  df2 %>% pivot_longer(!median_income, names_to = "variable", values_to = "value") %>%
    filter(variable!="avg_log" & variable!="stdev")
}

# Everything on the same plot
quantile_plot <- function(data, label ,log_scale=TRUE)
{
  p<-ggplot(data , aes(median_income,value, col=variable)) +
    scale_color_manual(values=c("avg" = "black","50%"="hotpink4","75%"="#BF80FF","90%"="#00AFBB","95%"="#E7B800", "99%"="#FC4E07"))+
    #scale_x_continuous(trans='log2')+
    geom_point() + 
    geom_line() +
    theme_minimal()+
    ggtitle(label)+
    #theme( legend.position = "none")+
    theme(plot.title = element_text(hjust = 0.5))+
    ylab('')+
    xlab('Household Income')+
    labs(colour = "Quantiles")
  if(log_scale) { p<- p + scale_y_continuous(trans = 'log10',limits=c(1,1400), breaks=c(1,10,100,1000))}
  else{p<- p + scale_y_continuous(breaks=c(0,50,100,150,200,250))}
  p
}

# save a feather or parquet instead
df <- read_parquet(fn_in) %>% filter(panel_year == 2018) %>%
  mutate(alcohol_tax = wine_tax + beer_tax + spirits_tax,
         median_income = (round(replace(median_income, median_income <12000, 10000) )),
         median_income = (round(replace(median_income, median_income >120000, 120000) )),
         drinks_per_week = (1000/(52*17.7)*ethanol /Adult),
         top10 = percent_rank(total_tax_but_ssb)> 0.9,
         top5 = percent_rank(total_tax_but_ssb)> 0.95)


df %>% group_by(median_income) %>% summarize( weighted_quantile(ethanol, w=projection_factor,probs=0.5))

total <- get_percentiles(df,'total_tax_but_ssb')
total2 <-total %>% make_long()

combined <- get_percentiles(df,'total_tax')
combined2 <- combined %>% make_long()

tobacco <- get_percentiles(df,'cigarette_tax')
tobacco2 <- tobacco %>% make_long() %>% 
          filter(variable!="50%"& variable!="75%") %>%
          mutate(value = replace(value, value <1, NA))

alcohol <- get_percentiles(df,'alcohol_tax')
alcohol2 <- alcohol %>% make_long()

ssb <- get_percentiles(df,'ssb_tax')
ssb2 <- ssb %>% make_long()

ethanol <- get_percentiles(df,'drinks_per_week')
ethanol2 <- ethanol %>% make_long()

# Drinks Per week Plot
quantile_plot(ethanol2,'',FALSE)+
  scale_y_continuous(breaks=c(0,5,10,20,30,40))+
  theme(legend.position="bottom")+
  ylab('Drinks Per Adult Per Week')
ggsave(file=fn_drinks, width=9, height=7)


d <- get_percentiles(df,'total_tax_but_ssb')
str1=paste("Corr:", toString(round(cor(d$median_income,d$avg),3)))
str2=paste("Corr:", toString(round(cor(d$median_income,d$avg_log),3)))
str3=paste("Corr:", toString(round(cor(d$median_income,d$stdev),3)))

# Most basic line chart
p1 <- ggplot(d, aes(x=median_income, y=avg)) +
  geom_point(size=2,color='black') +
  xlab("Household Income") +
  ylab("")+
  ggtitle("Average Sin tax Spending")+
  annotate("text", x = 80000, y = 32, label =str1 )+
  theme_minimal()

# Most basic line chart
p2 <- ggplot(d, aes(x=median_income, y=avg_log)) +
  geom_point( size=2, color='black') +
  xlab("Household Income") +  ylab("")+
  ggtitle("Average: Log(1+Sin tax Spending)")+
  annotate("text", x = 80000, y = 4.6, label =str2 )+
  theme_minimal()

# Most basic line chart
p3 <- ggplot(d, aes(x=median_income, y=stdev)) +
  geom_point(color='black') +
  xlab("Household Income") +  ylab("")+
  ggtitle("Standard Deviation")+
  annotate("text", x = 80000, y = 125, label =str3 )+
  theme_minimal()

p1+p2+p3
ggsave(file=fn_log_level, width=10, height=6)


