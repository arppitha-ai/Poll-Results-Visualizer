# Interview Preparation

## 30-second HR explanation
"I built a Poll Results Visualizer that takes messy survey data, cleans it, and turns it into charts, a written insights report and an interactive dashboard. It shows which option leads, how preferences differ by region and age, and what people say in comments. It mirrors what survey platforms like Qualtrics do, and I used synthetic data with deliberate errors to show real-world cleaning."

## 60-second technical explanation
"The pipeline has five modules: a seeded generator that creates a poll with hidden regional/age patterns and injected errors, a cleaning module that dedupes, standardises categories, validates Likert ratings and logs every change, an analysis module for vote share with margin of error, cross-tabs and rating stats, a visualization module that feeds both PNG exports and a combined dashboard, and an insights module that converts tables into sentences. A Streamlit app adds filters and CSV upload. I added pytest tests for cleaning and analysis."

## 10 questions
1. **Why this project?** Survey analysis is core to analyst roles; it covers cleaning, aggregation, visualization and communication end-to-end.
2. **Your data is synthetic, is that a problem?** No, I state it openly. Synthetic data let me plant known patterns and verify the pipeline recovers them, and the code works on real CSVs via `--input` or the dashboard upload.
3. **How did you clean the data?** Dropped exact duplicates; lower-cased/trimmed text and mapped variants (`powerbi`, `POWER BI`) to one label; converted ratings to numeric and rejected values outside 1-5; dropped rows missing critical fields, labelled optional blanks "Unknown"; logged counts per step.
4. **Why drop missing ratings but keep missing region?** Rating/tool are the core metrics, so without them a row is meaningless; region is only a segmentation field, so the row still counts in overall results.
5. **How do you know a lead is real?** Compute the 95% margin of error `1.96·√(p(1-p)/n)`. If the lead over second place is smaller than roughly the margin, call it too close to call.
6. **Which chart for which question type?** Multiple choice: bar (pie only for few options); Yes/No: donut; Likert: histogram/box plot; across segments: stacked bar or heatmap; time: line; text: word cloud + sentiment.
7. **Why percentages within each region (row-normalised)?** Raw counts are distorted by group size; row-wise percentages compare preference fairly between groups of different sizes.
8. **How does the sentiment analysis work and its limits?** A lexicon counts positive vs negative words. It's fast and explainable but misses negation ("not good"), sarcasm and context; next step would be VADER or a transformer model.
9. **What biases affect poll data?** Self-selection, non-response, sampling bias (shared among friends), leading questions, and small samples. I'd weight by demographics and report sample size and margin of error.
10. **How would you scale it?** Pull responses live via the Google Sheets/Forms API, store in PostgreSQL, schedule cleaning with Airflow/cron, cache analysis, deploy the dashboard on Streamlit Cloud or Docker, and add data-quality checks.

## Bonus quick answers
- **Biggest challenge?** Messy ratings like "four" or 7; solved with word mapping + range validation and logging.
- **What would you improve?** Significance tests, better NLP, real dataset, weighting.
- **Business value?** Cuts manual reporting time and gives stakeholders self-service filtering.
- **Key metrics?** Vote share, margin of error, average rating, % satisfied (4-5), recommend rate, sentiment mix, response trend.
