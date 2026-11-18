// One shared place for the band rules, so the REST endpoint and the batch job can never disagree.
public with sharing class LoanBands {

    // reviewCutoff: scores at or above it are flagged (our model's cost-based cut-off is 0.15).
    // highCutoff: scores at or above it are escalated as High.
    public static String bandFor(Decimal score, Decimal reviewCutoff, Decimal highCutoff) {
        if (score >= highCutoff)   { return 'High'; }
        if (score >= reviewCutoff) { return 'Medium'; }
        return 'Low';
    }
}