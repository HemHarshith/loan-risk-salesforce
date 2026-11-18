// Lightning Web Component: shows the risk score and band for one Loan Application record.
// It reads the record directly through Lightning Data Service, so no Apex code is needed here
// (Salesforce also handles caching, field-level security and refreshing for us).
import { LightningElement, api, wire } from 'lwc';
import { getRecord, getFieldValue } from 'lightning/uiRecordApi';

// Importing fields from the schema (instead of typing strings) makes Salesforce
// check at deploy time that the fields exist, and tracks them as dependencies.
import RISK_SCORE from '@salesforce/schema/Loan_Application__c.Risk_Score__c';
import RISK_BAND from '@salesforce/schema/Loan_Application__c.Risk_Band__c';
import CREDIT_AMOUNT from '@salesforce/schema/Loan_Application__c.Credit_Amount__c';
import PURPOSE from '@salesforce/schema/Loan_Application__c.Purpose__c';

export default class LoanRiskCard extends LightningElement {
    // Salesforce fills recordId automatically when the card sits on a record page.
    @api recordId;

    // @wire runs getRecord whenever recordId changes; "$recordId" means "use the current value".
    // The result lands in "loan" as { data, error }.
    @wire(getRecord, {
        recordId: '$recordId',
        fields: [RISK_SCORE, RISK_BAND, CREDIT_AMOUNT, PURPOSE]
    })
    loan;

    // The getters below are recalculated automatically whenever "loan" changes.
    get hasData() {
        return !!this.loan.data;
    }

    get hasError() {
        return !!this.loan.error;
    }

    // The model stores a probability from 0 to 1; people understand percentages better.
    get riskPercent() {
        const score = getFieldValue(this.loan.data, RISK_SCORE);
        return score === null || score === undefined ? 0 : Math.round(score * 1000) / 10;
    }

    get band() {
        return getFieldValue(this.loan.data, RISK_BAND) || 'Not scored';
    }

    get amount() {
        return getFieldValue(this.loan.data, CREDIT_AMOUNT);
    }

    get purpose() {
        return getFieldValue(this.loan.data, PURPOSE);
    }

    // Picks a built-in Salesforce badge colour: green (success), amber (warning), red (error).
    get badgeClass() {
        const colours = { Low: 'slds-theme_success', Medium: 'slds-theme_warning', High: 'slds-theme_error' };
        return 'slds-badge ' + (colours[this.band] || '');
    }

    // Plain-language advice for the loan officer. The 0.15 cut-off came from our cost analysis in Python.
    get advice() {
        if (this.band === 'High') {
            return 'High risk: escalate for manual review before approval.';
        }
        if (this.band === 'Medium') {
            return 'Flagged: above our 15% default-risk threshold, so review the application.';
        }
        if (this.band === 'Low') {
            return 'Below the review threshold: standard processing.';
        }
        return 'This loan has not been scored yet.';
    }
}