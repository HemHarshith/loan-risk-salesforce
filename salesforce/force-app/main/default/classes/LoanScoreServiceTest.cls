// Test class: Salesforce needs 75% code coverage to deploy, and tests prove the logic works.
// @IsTest data is rolled back automatically, so these records never stay in the org.
@IsTest
private class LoanScoreServiceTest {

    // Helper that builds one fake loan with a chosen score.
    private static LoanScoreService.LoanInput makeLoan(Decimal score) {
        LoanScoreService.LoanInput l = new LoanScoreService.LoanInput();
        l.age = 35; l.creditAmount = 5000; l.durationMonths = 24;
        l.purpose = 'new car'; l.riskScore = score;
        return l;
    }

    @IsTest
    static void savesRecordsWithCorrectBands() {
        List<LoanScoreService.LoanInput> inputs = new List<LoanScoreService.LoanInput>{
            makeLoan(0.05), makeLoan(0.30), makeLoan(0.80)
        };
        Test.startTest();
        LoanScoreService.Result r = LoanScoreService.createScored(inputs);
        Test.stopTest();

        System.assertEquals(3, r.created, 'Three loans should be created');
        List<Loan_Application__c> saved =
            [SELECT Risk_Band__c FROM Loan_Application__c ORDER BY Risk_Score__c];
        System.assertEquals('Low', saved[0].Risk_Band__c);
        System.assertEquals('Medium', saved[1].Risk_Band__c);
        System.assertEquals('High', saved[2].Risk_Band__c);
    }

    @IsTest
    static void rejectsEmptyList() {
        try {
            LoanScoreService.createScored(new List<LoanScoreService.LoanInput>());
            System.assert(false, 'Expected an exception for an empty list');
        } catch (LoanScoreService.ScoreException e) {
            System.assert(e.getMessage().contains('No loans'));
        }
    }

    @IsTest
    static void rejectsScoreOutOfRange() {
        try {
            LoanScoreService.createScored(new List<LoanScoreService.LoanInput>{ makeLoan(1.5) });
            System.assert(false, 'Expected an exception for a score above 1');
        } catch (LoanScoreService.ScoreException e) {
            System.assert(e.getMessage().contains('between 0 and 1'));
        }
    }
}