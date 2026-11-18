// Subscriber: runs every time a High_Risk_Loan__e event arrives.
// It runs asynchronously, as the "Automated Process" user, after the loan insert has been committed.
trigger HighRiskLoanTrigger on High_Risk_Loan__e (after insert) {

    // Build every Task in memory first, then insert once (never DML inside a loop: governor limits).
    List<Task> tasks = new List<Task>();
    for (High_Risk_Loan__e evt : Trigger.new) {
        tasks.add(new Task(
            Subject      = 'Review high-risk loan (' + evt.Risk_Band__c + ', score ' + evt.Risk_Score__c + ')',
            WhatId       = (Id) evt.Loan_Id__c,        // links the Task to the loan record
            OwnerId      = evt.CreatedById,            // the Automated Process user can't own tasks, so use the user who published
            Priority     = 'High',
            Status       = 'Not Started',
            ActivityDate = Date.today().addDays(2)));  // due in 2 days
    }
    insert tasks;
}