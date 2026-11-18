// Test class for the Batch Apex job. Test data is rolled back automatically after each test.
@IsTest
private class LoanBandBatchTest {

    @IsTest
    static void rebandsLoansWithNewCutoffs() {
        // Three loans with scores but no band yet.
        insert new List<Loan_Application__c>{
            new Loan_Application__c(Risk_Score__c = 0.05),
            new Loan_Application__c(Risk_Score__c = 0.18),
            new Loan_Application__c(Risk_Score__c = 0.80)
        };

        // New rule: review from 0.20, High from 0.50. So 0.18 must now become Low.
        Test.startTest();
        Database.executeBatch(new LoanBandBatch(0.20, 0.50), 200);
        Test.stopTest();   // forces the batch to finish before we check

        // ORDER BY makes the list order predictable: [0.05, 0.18, 0.80].
        List<Loan_Application__c> loans =
            [SELECT Risk_Band__c FROM Loan_Application__c ORDER BY Risk_Score__c];
        System.assertEquals(3, loans.size(), 'All three loans should exist');
        System.assertEquals('Low',  loans[0].Risk_Band__c, '0.05 is below the 0.20 review cut-off');
        System.assertEquals('Low',  loans[1].Risk_Band__c, '0.18 is below the new 0.20 cut-off');
        System.assertEquals('High', loans[2].Risk_Band__c, '0.80 is above the 0.50 High cut-off');
    }
}