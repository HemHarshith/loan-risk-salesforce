@IsTest
private class LoanRiskSummaryControllerTest {

    @IsTest
    static void summarisesBandsAndTopLoans() {
        insert new List<Loan_Application__c>{
            new Loan_Application__c(Risk_Score__c = 0.05, Risk_Band__c = 'Low'),
            new Loan_Application__c(Risk_Score__c = 0.30, Risk_Band__c = 'Medium'),
            new Loan_Application__c(Risk_Score__c = 0.80, Risk_Band__c = 'High')
        };

        Test.startTest();
        LoanRiskSummaryController ctrl = new LoanRiskSummaryController();
        Test.stopTest();

        System.assertEquals(3, ctrl.totalLoans, 'Three scored loans exist');
        System.assertEquals(3, ctrl.bandCounts.size(), 'One row per band');
        System.assertEquals('High', ctrl.bandCounts[0].band, 'High is listed first');
        System.assertEquals(1, ctrl.bandCounts[0].total);
        System.assertEquals('High', ctrl.topLoans[0].Risk_Band__c, 'Highest score comes first');
    }

    @IsTest
    static void handlesNoLoans() {
        LoanRiskSummaryController ctrl = new LoanRiskSummaryController();
        System.assertEquals(0, ctrl.totalLoans);
        System.assertEquals(0, ctrl.bandCounts[0].percent, 'No divide-by-zero error');
    }
}