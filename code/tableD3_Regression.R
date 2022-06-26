library("fixest")
library("tidyverse")
library("reshape2")
library("arrow")
# save a feather or parquet instead
df <- read_parquet("~/Dropbox/sin_tax_project/proc_data/cluster_data_all_years.parquet", header = TRUE)
df <- df[df$panel_year == 2018,]
fn_out <- '~/Dropbox/sin_tax_project/tables/tableD3.tex'

df$clusters <- as.factor(df$clusters)
df$income_group <- relevel( as.factor(df$income_group),ref='45,000-69,999')
df$race <- relevel( as.factor(df$race),ref='White')
df$age_group <- relevel(as.factor(df$age_group), ref = "over_65")
df$edu_group <- relevel(as.factor(df$edu_group),ref = "Graduated College")
df$presence_child<- as.factor(df$presence_child)

#log tax burden ~ log income + dummy
#choose cluser0, mid edu and mid income, white, nonhispanic as reference 
#First Column
model1a <- feols(log(total_tax_but_ssb+1) ~ 1+ income_group+ edu_group + race + Hispanic_Origin +presence_child + age_group
             | fips_state_desc, data = df, weights=df$projection_factor)
summary(model1a)


model0 <- feols(log(total_tax_but_ssb+1) ~ 1+ income_group , data = df, weights=df$projection_factor)
summary(model0)

model2a <- feols(log(total_tax_but_ssb+1) ~  1+ income_group+ edu_group + race + Hispanic_Origin +presence_child+ age_group
             | clusters+fips_state_desc, cluster = ~fips_state_desc + clusters, data = df, weights=df$projection_factor)
summary(model2a)

model2b <- feols(log(total_tax_but_ssb+1) ~  1+ income_group + i(clusters,log(median_income))+ edu_group + race + Hispanic_Origin +presence_child+ age_group
                 | clusters+fips_state_desc, cluster = ~fips_state_desc + clusters, data = df, weights=df$projection_factor)
summary(model2b)

model3a <- feols(log(total_tax+1) ~ 1+ income_group+ edu_group + race + Hispanic_Origin +presence_child+ age_group
             | fips_state_desc, data = df, weights=df$projection_factor)
summary(model3a)

model4a <- feols(log(total_tax+1) ~  1+ income_group+ edu_group + race + Hispanic_Origin +presence_child+ age_group
             | clusters+fips_state_desc, cluster = ~fips_state_desc + clusters, data = df, weights=df$projection_factor)
summary(model4a)


# For printing the table

order = c("Income: $<$ 24,999","Income:", "Race","Hispanic","Children","Edu: High School or Less",'Edu: Some College','Edu: Post College Grad','Age: Under 35','Age:')

setFixest_dict(c(raceBlack = "Race: Black", raceAsian = "Race: Asian",
                 raceOther = "Race: Other", Hispanic_OriginTRUE = "Hispanic: Yes",
                 presence_childTRUE="Children: Yes", edu_groupHighSchoolorLess="Edu: High School or Less",
                 edu_groupSomeCollege="Edu: Some College", edu_groupPostCollegeGrad="Edu: Post College Grad",
                 "income_group25,000-44,999"="Income: 25,000-44,999",
                 "income_group<24,999"="Income: $<$ 24,999",
                 
                 "income_group45,000-69,999"="Income: 45,000-69,999",
                 "income_group70,000-99,999"="Income: 70,000-99,999",
                 "income_group>100,000"="Income: $>$ 100,000", 
                 age_group35_to_44="Age: 35-44",age_group45_to_54='Age: 45-54',
                 age_group55_to_64='Age: 55-64', age_groupunder_35='Age: Under 35',
                 fips_state_desc="State", clusters='Cluster Assignment'))

etable(model1a,model2a,model3a,model4a, order=order, digits=3, digits.stats = 4,signifCode=NA, depvar=FALSE,
    subtitles = c("Log(Sin Tax)","Log(Sin Tax)","Log(Sin Tax+SSB Tax)","Log(Sin Tax+SSB Tax)"),
    style.tex = style.tex("aer",fixef.suffix = " FE"),tex = TRUE, file=fn_out, replace=TRUE)





 

