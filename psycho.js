function putquestion(Question, QuestionNum)
{
  document.write("<li><b> ... " + Question + "</b><br>")
  document.write("Disagree")
  document.write("&nbsp <input type=radio name=question[" + QuestionNum + "] value=1 checked>1")
  for (i=2; i<=5; i++) {
    document.write("&nbsp <input type=radio name=question[" + QuestionNum + "] value=" + i + ">" + i)
  }
  document.write("&nbsp Agree")
}
putquestion("is talkative", 1)
putquestion("does a thorough job", 2)
putquestion("is original, comes up with new ideas", 3)
putquestion("is helpful, unselfish with others", 4)
putquestion("can be somewhat careless", 5)
putquestion("is relaxed, handles stress well", 6)
putquestion("is curious about many things", 7)
putquestion("is full of energy", 8)
putquestion("starts quarrels with others", 9)
putquestion("is a reliable worker", 10)
putquestion("is a deep thinker", 11)
putquestion("tends to be disorganized", 12)
putquestion("worries a lot", 13)
putquestion("tends to be quiet", 14)
putquestion("tends to be lazy", 15)
putquestion("sometimes shy", 16)
putquestion("is sometimes rude to others", 17)
putquestion("tends to find fault with others", 18)
putquestion("gets nervous easily", 19)
putquestion("likes to work in a team", 20)