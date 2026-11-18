// Batch Apex: re-assigns Risk_Band__c on every scored loan using new cut-offs.
// Salesforce splits the work into chunks (default 200 records), and each chunk gets its own fresh
// set of governor limits. That is how large data volumes are processed safely.
// Database.Stateful keeps our counters alive between chunks (normally variables reset each chunk).
public with sharing class LoanBandBatch implements Database.Batchable<SObject>, Database.Stateful {

    private final Decimal reviewCutoff;
    private final Decimal highCutoff;
    public Integer scanned = 0;
    public Integer changed = 0;
    public Integer failed  = 0;

    public LoanBandBatch(Decimal reviewCutoff, Decimal highCutoff) {
        this.reviewCutoff = reviewCutoff;
        this.highCutoff   = highCutoff;
    }

    // start: runs once and says which records to process. A QueryLocator can handle up to 50 million rows.
    public Database.QueryLocator start(Database.BatchableContext bc) {
        return Database.getQueryLocator(
            [SELECT Id, Risk_Score__c, Risk_Band__c FROM Loan_Application__c WHERE Risk_Score__c != null]);
    }

    // execute: runs once per chunk. We update only the records whose band actually changes.
    public void execute(Database.BatchableContext bc, List<Loan_Application__c> scope) {
        List<Loan_Application__c> toUpdate = new List<Loan_Application__c>();
        for (Loan_Application__c loan : scope) {
            scanned++;
            String newBand = LoanBands.bandFor(loan.Risk_Score__c, reviewCutoff, highCutoff);
            if (newBand != loan.Risk_Band__c) {
                loan.Risk_Band__c = newBand;
                toUpdate.add(loan);
            }
        }
        // allOrNone = false: one bad record doesn't block the rest of the chunk; we count the failures.
        for (Database.SaveResult r : Database.update(toUpdate, false)) {
            if (r.isSuccess()) { changed++; } else { failed++; }
        }
    }

    // finish: runs once at the end. The debug line shows in the Apex log.
    public void finish(Database.BatchableContext bc) {
        System.debug('LoanBandBatch done. scanned=' + scanned + ' changed=' + changed + ' failed=' + failed);
    }
}