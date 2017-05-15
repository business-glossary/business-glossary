title: Commenting
published: 2016-12-08
tags: [sas, standards]

# Overview

This article describes the convention to follow when commenting SAS program code.

# Program Header

For a program header comment block that is parseable to produce automated program documentation, I favour something along these lines:

```java
/* 
  PROGRAM INFORMATION 
    PROJ: Account Management
    DESC: Provides aggregated program documentation. 
    AUTH: Alan Tindale <alan.tindale@boq.com.au> 
    DATE: 2016-11-08 
 
  INPUTS/OUTPUTS 
    INs : A base directory. 
    OUTs: HTML file in base directory.
     
  MODIFICATIONS 
    2016-01-19 Alan Tindale <alan.tindale@boq.com.au>  
      (+) Added section headers. 
    2015-09-21 Alan Tindale <alan.tindale@boq.com.au>  
      (+) Added a proc datasets to clean up temp datasets. 
      (+) Added a data null step to generate html report. 
    2015-08-31 Alan Tindale <alan.tindale@boq.com.au> 
      (+) Added code line number. 
      (+) Added view combining file listing and detail listing. 
    2015-08-30 Alan Tindale <alan.tindale@boq.com.au> 
      (+) Accommodate arguments of macro programs. 
    2015-08-26 Alan Tindale <alan.tindale@boq.com.au> 
      (+) Filelist dataset includes only .sas programs. 
    2015-08-25 Alan Tindale <alan.tindale@boq.com.au> 
      (+) Added prog_doc dataset. 
      (-) Removed SQL proc to get paths and filenames. 
      (*) Fixed filesize field. 
*/
```

The modification history is, of course, not really necessary with version control but the above is a nice concise format (+ = addition, - = removed, * = updated).

The attributes listed can be extended as needed.

# General Commenting

In regards to general commenting throughout code, I favour liberal use of comment blocks like this :

```
/********************************************************************************
**                                                                             **
** Return the log back to default position and remove options applied.         **
**                                                                             **
********************************************************************************/
```

The above would separate out a larger process containing multiple data or procedure steps. You may add double lines and a section name/number for additional impact.

```
/********************************************************************************
*********************************************************************************
**                                                                             **
** 010 Wash Names                                                              **
**                                                                             **
** Collect some data as an encapsulated process.                               **
**                                                                             **
*********************************************************************************
********************************************************************************/
```


If used within a macro (contents of the macro should be indented by four spaces) then the comment block should be indented in line.

```
%macro do_something;

    ...some code...

    /****************************************************************************
    ** 9.  Produce the activity report.                                        **
    ****************************************************************************/
```

Within a data step commenting of logic would be like this:

```
data hello_world;
    set sashelp.prdsale;

    /* Multiple sales by an abstract fudge-factor defined by a random number generator */
    fictional_balance = balance * 0.4576;
run;
```

As you can see from the above I predominately favour `/* */` commenting and shy away from `* ;` style.

# Inline Comments

Use inline comments sparingly.

An inline comment is a comment on the same line as a statement. Inline comments should be separated by at least two spaces from the statement. They should use the form `/* */`.

# Comment Text

Comments that contradict the code are worse than no comments. Always make a priority of keeping the comments up-to-date when the code changes!

Comments should be complete sentences. If a comment is a phrase or sentence, its first word should be capitalized.

If a comment is short, the period at the end can be omitted. Block comments generally consist of one or more paragraphs built out of complete sentences, and each sentence should end in a period.

# Tagging of Terms and Rules

To tag logic so can it can be parsed, captured and then surfaced by the Business Glossary I have in mind a somewhat similar scheme to the program header.

```
data hello_world;
    set sashelp.prdsale;

    /* RULE_START: Sales Fudge Factor
       Multiple sales by an abstract fudge-factor defined by a random number generator */
    fictional_balance = balance * 0.4576;
    /* RULE_END */
run;
```

The parser (once written) will place what is in the between the start and end tags into the notes section in the Glossary.

The actual solution is likely to implement multiple notes per rule so that many sections of code can be captured.

Again, I am still playing with ideas at the moment and have not developed anything. I don’t want to specify something that becomes too onerous.

As an aside and related to this I have written a batch loader that loads the Glossary through a yaml file format, an example of which is:

```yaml
---
rules:
-
    identifier: BR_004
    name: Days in Arrears Adjustment
    description: |
       Corrects an issue where the number of months past due is calculated incorrectly when the 
        reference date is the 30th or 31st of January, due to there being less days in February.
    notes: |
        **Rule:**
        If the reference date is the 30th or 31st January then add one to the number of days in arrears to 
        cater for: at the end of February (28th or 29th, 28th when error is produced?), The account will 
        only have been in arrears for 29 days and will thus be sorted into the delinquency bucket indicating 
        one missed payment. In reality if the account reaches the end of Febuary and is still delinquent, it 
        should be sorted into the delinquency bucket indicating two missed payments?
        
        Located: Account_Management\4.0_Staging_Tables_FACT\acc_hist_ext.sas
        ```
        /* calculate days in arears secondary (TA) adjustments for February */
        CASE WHEN rd.Month eq 1 AND rd.DayOfMonth IN (30, 31) THEN ahe.DAYS_IN_ARREARS + 1
             ELSE                                                  ahe.DAYS_IN_ARREARS
        END as DAYS_IN_ARREARS,
        ```
    terms: 
        - Arrears
```


