<html>
<head>
<script>
function scrollTo(hash) {
    location.hash = "#" + hash;
}
</script>
</head>
<body>
<pre>

%macro buildACCT_HIST(SourceLib = , year = );

	/*	ACCT2004 does not have ApplicationNumber and various other differences */
	/* 1 DUPE FOUND IN MAY 2004 DUE TO BAD OFFSET ACCOUNT NUMBER CHANGE */
	/* VARIOUS FIELDS ADDED OVER THE YEARS */

	
	
	
	PROC SQL;
	CREATE TABLE STAGING.TEMP_ACCT_HIST AS
	SELECT   d.FullDate							AS K_TIME
	        ,a.Region							AS REGION
	        ,a.accno							AS ACCOUNT_NO
			,a.applicationnumber				AS APPLICATIONNUMBER
	        ,a.status							AS STATUS
			,a.brkrno							AS BROKERNUMBER
	        ,a.bsb								AS BSB
	        ,a.accbal							AS ACCOUNT_BALANCE
	        ,a.loan_amt							AS LOAN_AMT
			,a.d_bal							AS AverageDailyBalance
			,a.d_bal_Actual						AS ActualDailyAverageBalance
			,a.int_rate							AS InterestRate
			,a.margin							AS MarginPercentage
			,a.Net_int							AS NetInterest
	        ,a.Branch							AS Branch
	        ,a.SHRT_NME							AS SHORT_NAME
	        ,case when a.DaysInArrears ge 0 then a.DaysInArrears
                  else 0
             end								AS DAYS
	        ,a.ICBS_prodcode					AS ICBS_CODE
	        ,a.DateLoanApproval					AS APPROVAL_DATE
	        ,a.open_dte							AS OPEN_DATE
			,a.DateLastStatement				AS LastStatementDate
	        ,a.mat_dte							AS MATURITY_DATE
	        ,a.OD_LIMIT							AS OVERDRAFT_LIMIT
			,a.LimitExpiryDate					AS LimitExpiryDate
			,a.offset_com_dte					AS OffsetCommencementDate
			,a.offset_accno						AS OffsetAccountNumber
			,a.offset_int						AS OffsetInterest_Rate
			,a.offset_flag						AS OffsetClassification
	        ,a.arrears							AS SCHEDULED_BALANCE
	        ,a.repaymt							AS REPAYMENT_AMOUNT
	        ,a.AccBalFlag						AS AccBalFlag
	        ,a.B_Type							AS BRANCH_TYPE
	        ,a.LowDocLoanInd					AS LOW_DOC_LOAN_IND
			%if &year gt 2004 %then %do;
	        ,a.CCI_Ind							AS ConsumerCreditInsuranceInd
			%end;
			%if &year gt 2005 %then %do;
			,a.NextPaymentDate					AS NextPaymentDate
	        ,a.ReviewDate						AS REVIEW_DATE
			,a.PendingProductSwitchDate			AS PendingProductSwitchDate        
	        ,a.LQRCode							AS LQR_CODE   
	        ,a.Brand							AS Brand
			%end;
			%if &year gt 2009 %then %do;
			,a.ConvertedAccount					AS CONVERTEDACCOUNT 
			,a.MinimumBalanceThisCycle			AS MinimumBalanceThisCycle
			%end;
			%if &year gt 2011 %then %do;
	        ,a.TopUpTxnAmt						AS TOPUP_AMT 
			,a.LoanAmt_Orig						AS OriginalLoanAmount 
			,a.DRMargin							AS DRMargin
			%end;
			%if &year gt 2012 %then %do;
			,a.aggregatorno						AS AggregatorNumber
			%end;
			%if &year gt 2013 %then %do;
			,a.DealerCIFNumber					AS DealerCIFnumber
			,a.GroupCIFNumber					AS GroupCIFnumber
			%end;
	FROM     CRASL.v_ref_month as d
	         join &SourceLib..ACCT&year. AS a
	          on (input(a.year,12.) = d.FiscalYear and 
	              a.month = d.FiscalMonth)
	%if &year eq 2004 %then %do;
    WHERE    NOT (a.Year = '2004' AND a.Month=9 AND a.ACCNO=90403700 AND a.offset_accno=80403700)
	%end;
	union
	SELECT   bg.K_TIME
	        ,''									AS REGION
	        ,bg.ACCOUNT_NO
			,bg.ApplicationNumber
	        ,''									AS STATUS
			,''									AS BROKERNUMBER
			,bg.BSB
			,bg.balance							as ACCOUNT_BALANCE
			,bg.LOAN_AMT										
			,.									AS AverageDailyBalance
			,.									AS ActualDailyAverageBalance
			,.									AS InterestRate
			,.									AS MarginPercentage
			,.									AS NetInterest
	        ,''									AS Branch
	        ,''									AS SHORT_NAME
			,.									as DAYS
            ,bg.ICBS_CODE
	        ,.									AS APPROVAL_DATE
	        ,bg.open_date
			,.									AS LastStatementDate
	        ,bg.MATURITY_DATE
			,.									as OVERDRAFT_LIMIT	
			,.									AS LimitExpiryDate
			,.									AS OffsetCommencementDate
			,.									AS OffsetAccountNumber
			,.									AS OffsetInterest_Rate
			,''									AS OffsetClassification
	        ,bg.balance							AS SCHEDULED_BALANCE
	        ,.									AS REPAYMENT_AMOUNT
	        ,''									AS AccBalFlag
	        ,''									AS BRANCH_TYPE
	        ,.									AS LOW_DOC_LOAN_IND
			%if &year gt 2004 %then %do;
	        ,''									AS ConsumerCreditInsuranceInd
			%end;
			%if &year gt 2005 %then %do;
			,.									AS NextPaymentDate
	        ,bg.REVIEW_DATE
			,.									AS PendingProductSwitchDate        
	        ,''									AS LQR_CODE   
	        ,''									AS Brand
			%end;
			%if &year gt 2009 %then %do;
			,''									AS CONVERTEDACCOUNT 
			,.									AS MinimumBalanceThisCycle
			%end;
			%if &year gt 2011 %then %do;
	        ,.									AS TOPUP_AMT 
			,.									AS OriginalLoanAmount 
			,.									AS DRMargin
			%end;
			%if &year gt 2012 %then %do;
			,''									AS AggregatorNumber
			%end;
			%if &year gt 2013 %then %do;
			,''									AS DealerCIFnumber
			,''									AS GroupCIFnumber
			%end;
	FROM     CRASL.v_ref_month as vrm
			 join CRASL.ACCT_hist_BG AS bg
			  on (vrm.FullDate eq bg.k_time)
	where    vrm.FiscalYear eq &year.
	and		 vrm.fullDate le today()
/*	ORDER BY d.FullDate*/
/*			,a.accno*/
	;
	QUIT;

	</pre><a name="location">Calculation for LGD here:</a><pre>

	PROC SQL;
		CREATE UNIQUE INDEX TIMEACC ON STAGING.TEMP_ACCT_HIST (K_TIME, ACCOUNT_NO, APPLICATIONNUMBER);
	QUIT;
	/* if the temp table was created successfully then we can append to target table */
    %if %sysfunc(exist(STAGING.TEMP_ACCT_HIST)) %then %do;

		/* check the target table exists - if first time then create it */
    	%if %sysfunc(exist(CRASL.ACCT_HIST_&year.)) %then %do;
			proc sql;
			create table CRASL.ACCT_HIST_&year. as
			select * from CRASL.ACCT_HIST_&year.
			;
			quit;

			/* if the table has been created then Nuke the data for this this time period */
			PROC SQL;
				DROP INDEX K_TIME ON CRASL.ACCT_HIST_&year.;
				DROP INDEX ACCOUNT_NO ON CRASL.ACCT_HIST_&year.;
			QUIT;
			%NukeData(dsname=CRASL.ACCT_HIST_&year.,
			      WhereClause=k_time IN (select distinct K_Time from STAGING.TEMP_ACCT_HIST),
			      SQLorDATASTEP=SQL);
			%if ( "%upcase(&NukeData_ErrInd)" = "Y" ) %then %goto exit;
			/* if the Nuke worked then append the data for this time period */
			proc append base = CRASL.ACCT_HIST_&year. data = STAGING.TEMP_ACCT_HIST force ;
			quit;
			PROC SQL;
				CREATE INDEX K_TIME ON CRASL.ACCT_HIST_&year. (K_TIME);
				CREATE INDEX ACCOUNT_NO ON CRASL.ACCT_HIST_&year. (ACCOUNT_NO);
			QUIT;
		%end;
		%else %do; 
		    /* if the target table does not exist then we can use proc append to create it */
			proc append base = CRASL.ACCT_HIST_&year. data = STAGING.TEMP_ACCT_HIST ;
			quit;
			PROC SQL;
				CREATE INDEX K_TIME ON CRASL.ACCT_HIST_&year. (K_TIME);
				CREATE INDEX ACCOUNT_NO ON CRASL.ACCT_HIST_&year. (ACCOUNT_NO);
			QUIT;
		%end;
    %end;
	/* clean up */
    proc sql;
		drop table STAGING.TEMP_ACCT_HIST;
	quit;
%exit:
%mend;

PROC SQL;
	drop view CRASL.ACCT_HIST;
QUIT;

%buildACCT_HIST(SourceLib = DETAIL, year=&CURR_FY.);

*%buildACCT_HIST(SourceLib = DETAIL, year=2016);
*%buildACCT_HIST(SourceLib = DETAIL, year=2015);
*%buildACCT_HIST(SourceLib = DETAIL, year=2014);
*%buildACCT_HIST(SourceLib = DETAIL, year=2013);
*%buildACCT_HIST(SourceLib = DETAIL, year=2012);
*%buildACCT_HIST(SourceLib = DETAIL, year=2011);
*%buildACCT_HIST(SourceLib = DETAIL, year=2010);
*%buildACCT_HIST(SourceLib = DETAIL, year=2009);
*%buildACCT_HIST(SourceLib = DETAIL, year=2008);
*%buildACCT_HIST(SourceLib = DETAIL, year=2007);
*%buildACCT_HIST(SourceLib = DETAIL, year=2006);
*%buildACCT_HIST(SourceLib = DETAIL, year=2005);
*%buildACCT_HIST(SourceLib = DETAIL, year=2004);


data CRASL.ACCT_HIST / view=CRASL.ACCT_HIST; 
			set	CRASL.ACCT_HIST_2016
				CRASL.ACCT_HIST_2015
				CRASL.ACCT_HIST_2014
				CRASL.ACCT_HIST_2013
				CRASL.ACCT_HIST_2012
				CRASL.ACCT_HIST_2011
				CRASL.ACCT_HIST_2010
				CRASL.ACCT_HIST_2009
				CRASL.ACCT_HIST_2008
				CRASL.ACCT_HIST_2007
				CRASL.ACCT_HIST_2006
				CRASL.ACCT_HIST_2005
;
run;
</pre>
</body>
</html>
