# nlp-sql
1. Download the pre-trained model from
https://github.com/naver/sqlova/releases/download/SQLova-parameters/model_bert_best.pt
https://github.com/naver/sqlova/releases/download/SQLova-parameters/model_best.pt

Place `model_best.pt` and `model_bert_best.pt` under `./`

2. Download the support files (which include the bert_config_uncased__.json and vocab_uncased_.txt) from
https://drive.google.com/file/d/1iJvsf38f16el58H4NPINQ7uzal5-V4v4/view
Place all the support files under `./param`

3. Download corenlp from
https://stanfordnlp.github.io/CoreNLP/history.html

4. Change the 'CORENLP_HOME' path in annotate_ws.py, 
`os.environ['CORENLP_HOME'] = "REPLACE_WITH_CORENLP_PATH"` in line 14.

5. Set up your MySQL database with host, port, user, password and the database ready.
> Make sure each table in your db has at least one row of data.

6. Running CoreNLP server, cd to your CoreNLP directory, in the example it might stanford-corenlp-4.5.2
```
java -mx4g -cp "*" edu.stanford.nlp.pipeline.StanfordCoreNLPServer -port 9000 -timeout 15000
```

7. Running script.py with specifying the required params(please replace the required params with your own):
```
python3 script.py -H HOST_NAME -p PORT_NUMBER -u USER_NAME -P PASSWORD -d DB_NAME
"-H", "--host"; "-p", "--port"; "-u", "--user"; "-P", "--password"; "-d", "--database"
```
