This project contains all files for the voicequery project.

## Organization

### Under "webapp" you will find the react app for the frontend of the application, also known as the "Lexicon Console". See that folder's readme for a list of available scripts

### Under "nltk-experiments" you will find several NLP scripts using they python nltk library

## Description

This application is being developed to solve the core business problem of using stored data from transactional systems and business warehouses to automatically provide answers to human-speech and text questions about that data.

The design will be broken up into several components:
  1. A query processor, which, using common libraries and NLP tools, will tokenize incoming business queries into (at least) the following 3 pieces:
  
    -Subjects (the "target" of the question, such as a business asset or record.
    
    -Conditions (which are parts of the sentence which are intended to act as data "filters" such as "during black friday" or "last week" or basic descriptors like "queen-sized" or "red".
    
    -Quantifiers (Usually at the start of the question and define the overall query type, such as "How many" or "What is the average" or "When did".
    
    
  2. An "Lexicon Console", the current portion of the app that is furthest develop and found in the "webapp" folder.  In this console, the user defines the "business lexicon."  Business lexicon can be either subjects or conditions, and represents business-specific terminology such as time period names only relevant to the business, or asset categories specific to the industry.  This console allows users to drag-and-drop business lexicon onto corresponding fields and field values from a referenced database, and stores these relationships as "concepts".  For example, a user might drag the "rented" business lexicon condition onto the "rental" field value of the "transaction type" field in order to create a relationship, informing that when a user uses the term "rented" in a business query, it should filter table data only to records which have the "renta" value in the "transaction type" field.
  
  A key back-end portion of the admin console will be a simple database table analyzer which will look through the contents of a connected table, enumerate the fields and their corresponding data types, find common field values (which will often imply drop-downs or other multi-select options from the source transactional system), and will send that field and value data to the admin console in the form of a JSON payload.
  
  3. A query "responder".  A human asks a question, either in spoken word or text. Using the tokenized data from the query processor, as well as the stored relationships created by the users the Lexicon Console, the responder will form database queries in order to select data required to answer the question, then will use the returned data selection to find a specific answer using code (python).  The response will come in the form of the simple human-audible answer as listed below in the case of a user only interacting via voice (on a VUI) or will show a simple chart if the user is on a system with a display.
  
This responder component is easier to demonstrate with an example.  In this example, imagine the current date is 6/20/19 and the questioner works for a rental department for costumes and other apparel.


### Question:
What costumes were rented the least in the last 2 years?

Logic:

costumes = lexicon entry for “costume” in the “asset_department” field

rented = lexicon entry for “rental” in the “transaction_type” field 

last week = 6/20/19 through 6/20/19


### Resulting SQL:

SELECT rental_transaction_id, rental_transaction_out_date, asset_id, asset_description

FROM rental_transactions

INNER JOIN assets

ON rental_transactions.asset_id = assets.asset_id

WHERE rental_transaction_out_date BETWEEN #6/20/17# AND #6/20/19#;

WHERE asset_department = (costume)


### Operations to perform in code:

Count number of transactions per costume asset

Find 5 assets with the minimum number of transactions

Create and return simple human-audible answer: "The 5 least utilized costume assets rented in the last 2 years were: A, B, C, D, and E" (where A-E represent the costume asset names.)

Create visual: produce table with bottom 5 or 10% of transaction counts

  
    
