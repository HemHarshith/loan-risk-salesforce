// REST endpoint that receives scored loans from Python and saves them as Loan_Application__c records.
// URL once deployed: <your-org-url>/services/apexrest/loanscore
// "global" is required for REST classes and for any inner class used in the request or response.
@RestResource(urlMapping='/loanscore/*')
global with sharing class LoanScoreService {

    // One loan as sent by Python. The field names must match the JSON keys exactly.
    global class LoanInput {
        public Integer age;
        public Decimal creditAmount;
        public Integer durationMonths;
        public String purpose;
        public Decimal riskScore;   // model probability of default, 0 to 1
    }

    // What we send back to the caller.
    global class Result {
        public Integer created;
        public List<Id> ids;
    }

    // Our own error type so callers get a clear message instead of a vague failure.
    public class ScoreException extends Exception {}

    // Turns the model score into a band. 0.15 is the cost-based threshold chosen in Python (script 03).
    // So Medium and High are the loans the model flags for review.
    @TestVisible
    private static String bandFor(Decimal score) {
        return LoanBands.bandFor(score, 0.15, 0.5);
    }

    // @HttpPost = runs when someone sends a POST request to the URL above.
    // The JSON body looks like {"loans": [ {...}, {...} ]}; "loans" matches this parameter name.
    @HttpPost
    global static Result createScored(List<LoanInput> loans) {
        // Validate first: reject empty input and oversized batches (a DML limit protects us anyway).
        if (loans == null || loans.isEmpty()) {
            throw new ScoreException('No loans supplied.');
        }
        if (loans.size() > 1000) {
            throw new ScoreException('Send at most 1000 loans per request.');
        }

        // Build all records in memory first, then insert once. Never run DML inside a loop (governor limits).
        List<Loan_Application__c> records = new List<Loan_Application__c>();
        for (LoanInput l : loans) {
            if (l.riskScore == null || l.riskScore < 0 || l.riskScore > 1) {
                throw new ScoreException('riskScore must be between 0 and 1.');
            }
            records.add(new Loan_Application__c(
                Applicant_Age__c   = l.age,
                Credit_Amount__c   = l.creditAmount,
                Duration_Months__c = l.durationMonths,
                Purpose__c         = l.purpose == null ? null : l.purpose.abbreviate(50),
                Risk_Score__c      = l.riskScore.setScale(3),   // field holds 3 decimal places
                Risk_Band__c       = bandFor(l.riskScore)
            ));
        }
        insert records;   // one DML statement for the whole batch

        // Publish one event per High-band loan. Ids exist only after the insert, so this must come after it.
        List<High_Risk_Loan__e> events = new List<High_Risk_Loan__e>();
        for (Loan_Application__c rec : records) {
            if (rec.Risk_Band__c == 'High') {
                events.add(new High_Risk_Loan__e(
                    Loan_Id__c = rec.Id, Risk_Score__c = rec.Risk_Score__c, Risk_Band__c = rec.Risk_Band__c));
            }
        }
        if (!events.isEmpty()) {
            EventBus.publish(events);   // one call for the whole list
        }

        Result r = new Result();
        r.created = records.size();
        r.ids = new List<Id>(new Map<Id, Loan_Application__c>(records).keySet());
        return r;
    }
}