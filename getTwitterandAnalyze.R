library(twitteR)
library(tm)
library(sentiment)
library(stargazer)

repecnames <- read.csv('postrmpdata_firsthalf.csv',fileEncoding='utf-8')

repecnames$num.tweets <- NA
repecnames$sentiment <- NA
repecnames$av.length <- NA


setup_twitter_oauth(apikey, apisecret, accesstoken, accesssecret)

removeURL <- function(x) gsub("http[^[:space:]]*", "", x)
removeat <- function(x) gsub("@[^[:space:]]*", "", x)

for (i in 1:dim(repecnames)[1]) {
  tweets <- try(userTimeline(repecnames$twitter[i],n=100))
  if (class(tweets) == 'list' & length(tweets) > 0) {
    tweets.df <- twListToDF(tweets)
    repecnames$num.tweets[i] <- dim(tweets.df)[1]
    
    #Remove URLs and @s
    tweets.df$text <- removeURL(removeat(tweets.df$text))
    
    sentiments <- try(sentiment(tweets.df$text))
    if (class(sentiments) == 'data.frame') {
      repecnames$sentiment[i] <- sum(sentiments$polarity=='positive')-sum(sentiments$polarity=='negative')
    }
    
    repecnames$av.length[i] <- mean(nchar(tweets.df$text))
  }
  else {
    repecnames$num.tweets[i] <- 0
  }
  Sys.sleep(1)
  print(paste("Working on ",repecnames$name[i]," who is ",i," of 1443 at ",Sys.time(),sep=''))
}

save(repecnames,file='econtwit.Rda')


library(tidyverse)
repecnames <- mutate(repecnames,av.sent = sentiment/num.tweets)
stargazer(select(repecnames,-RMPID) %>% 
            rename(RMP.rating = overall.rating,
                   num.RMP.reviews = num.reviews,
                   av.tweet.length = av.length,
                   av.tweet.sentiment = av.sent),type='text')

ggplot(repecnames,aes(x=av.sent))+stat_density(geom='line',col='blue')+
  xlab('Average Tweet Sentiment (1 = Positive, -1 = Negative)')+
  ylab('Density')
  labs(title='Basic Sentiment Analaysis on Econ Twitter',
       caption='Sentiment based on last 100 available tweets using sentiment140, handle list from RePeC')

ggplot(filter(repecnames,!is.na(overall.rating)),aes(x=av.sent,y=overall.rating))+geom_point()+
  geom_smooth(method='lm')+
  xlab('Average Tweet Sentiment (1 = Positive, -1 = Negative)')+
  ylab('RateMyProfessor Rating')
  labs(title='Tweet Sentiment and RateMyProfessor Rating',
       caption='Sentiment based on last 100 available tweets using sentiment140, handle list from RePeC\nGroup with nonmissing RMP ratings *highly* selected.')
