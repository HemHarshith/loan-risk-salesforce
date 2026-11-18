from pathlib import Path

# Salesforce metadata files are XML. NS is the required XML namespace.
NS = 'xmlns="http://soap.sforce.com/2006/04/metadata"'
BASE = Path("salesforce/force-app/main/default")
OBJ = "Loan_Application__c"          # "__c" means custom object/field
OBJ_DIR = BASE / "objects" / OBJ

def write(path, body):
    """Create folders if needed, then save one XML file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('<?xml version="1.0" encoding="UTF-8"?>\n' + body, encoding="utf-8")

# Picklist = dropdown with fixed values (Low / Medium / High)
band_values = "".join(
    f"<value><fullName>{v}</fullName><default>false</default><label>{v}</label></value>"
    for v in ["Low", "Medium", "High"])
band_xml = ("<valueSet><restricted>true</restricted><valueSetDefinition><sorted>false</sorted>"
            + band_values + "</valueSetDefinition></valueSet>")

# Each field: (API name, label, type, extra settings)
# precision = total digits, scale = digits after the decimal point
fields = [
    ("Applicant_Age__c",   "Applicant Age",     "Number",   "<precision>3</precision><scale>0</scale>"),
    ("Credit_Amount__c",   "Credit Amount",     "Number",   "<precision>18</precision><scale>2</scale>"),
    ("Duration_Months__c", "Duration (Months)", "Number",   "<precision>3</precision><scale>0</scale>"),
    ("Purpose__c",         "Purpose",           "Text",     "<length>50</length>"),
    ("Risk_Score__c",      "Risk Score",        "Number",   "<precision>4</precision><scale>3</scale>"),  # 0.000-1.000 probability from the model
    ("Risk_Band__c",       "Risk Band",         "Picklist", band_xml),
]

# 1) The object. AutoNumber gives each record a name like LA-0001.
write(OBJ_DIR / f"{OBJ}.object-meta.xml", f"""<CustomObject {NS}>
  <label>Loan Application</label><pluralLabel>Loan Applications</pluralLabel>
  <nameField><label>Application Number</label><type>AutoNumber</type>
    <displayFormat>LA-{{0000}}</displayFormat><startingNumber>1</startingNumber></nameField>
  <deploymentStatus>Deployed</deploymentStatus><sharingModel>ReadWrite</sharingModel>
</CustomObject>""")

# 2) One file per field
for api, label, ftype, extra in fields:
    write(OBJ_DIR / "fields" / f"{api}.field-meta.xml", f"""<CustomField {NS}>
  <fullName>{api}</fullName><label>{label}</label><type>{ftype}</type>{extra}
  <required>false</required>
</CustomField>""")

# 3) Permission set: gives access to the object and every field (FLS)
field_perms = "".join(
    f"<fieldPermissions><editable>true</editable><field>{OBJ}.{api}</field><readable>true</readable></fieldPermissions>"
    for api, *_ in fields)
write(BASE / "permissionsets" / "Loan_Risk_Access.permissionset-meta.xml", f"""<PermissionSet {NS}>
  <label>Loan Risk Access</label><hasActivationRequired>false</hasActivationRequired>
  <objectPermissions><allowCreate>true</allowCreate><allowDelete>true</allowDelete><allowEdit>true</allowEdit>
    <allowRead>true</allowRead><modifyAllRecords>true</modifyAllRecords><object>{OBJ}</object>
    <viewAllRecords>true</viewAllRecords></objectPermissions>
  {field_perms}
</PermissionSet>""")

print("Metadata files written to", BASE)