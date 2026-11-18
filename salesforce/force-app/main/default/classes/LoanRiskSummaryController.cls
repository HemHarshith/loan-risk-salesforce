// Controller for the Visualforce page. A controller is the Apex class that prepares the data a page shows.
// "with sharing" makes the code respect the current user's record access.
public with sharing class LoanRiskSummaryController {

    // A small helper class: one row of the "loans by band" table.
    public class BandCount {
        public String band    { get; set; }
        public Integer total  { get; set; }
        public Decimal percent { get; set; }
    }

    // Properties the page reads. "private set" means only this class may change them.
    public List<BandCount> bandCounts      { get; private set; }
    public List<Loan_Application__c> topLoans { get; private set; }
    public Integer totalLoans              { get; private set; }

    // The constructor runs when the page opens.
    public LoanRiskSummaryController() {
        load();
    }

    @TestVisible
    private void load() {
        // Aggregate query: COUNT per band in ONE query (cheaper than counting records in a loop).
        Map<String, Integer> counts = new Map<String, Integer>();
        totalLoans = 0;
        for (AggregateResult ar : [
                SELECT Risk_Band__c band, COUNT(Id) total
                FROM Loan_Application__c
                WHERE Risk_Band__c != null
                GROUP BY Risk_Band__c]) {
            Integer n = (Integer) ar.get('total');
            counts.put((String) ar.get('band'), n);
            totalLoans += n;
        }

        // Always show High, Medium, Low in that order, even when a band is empty.
        bandCounts = new List<BandCount>();
        for (String band : new List<String>{ 'High', 'Medium', 'Low' }) {
            BandCount bc = new BandCount();
            bc.band  = band;
            bc.total = counts.containsKey(band) ? counts.get(band) : 0;
            // Guard against dividing by zero when no loans exist yet.
            bc.percent = totalLoans == 0 ? 0 : (Decimal.valueOf(bc.total) * 100 / totalLoans).setScale(1);
            bandCounts.add(bc);
        }

        // The ten loans with the highest risk score, for a quick review list.
        topLoans = [
            SELECT Id, Name, Risk_Band__c, Risk_Score__c, Credit_Amount__c, Purpose__c
            FROM Loan_Application__c
            WHERE Risk_Score__c != null
            ORDER BY Risk_Score__c DESC
            LIMIT 10];
    }
}