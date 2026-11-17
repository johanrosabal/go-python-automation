# Real-World Locator Engineering Examples

This reference document demonstrates how the `smart-selenium-locator-generator` skill transforms brittle, positional selectors into robust, semantic Selenium locators.

---

## Example 1: Bootstrap / Traditional Form Group (Label with `for`)

### Raw HTML:
```html
<div class="form-group row">
  <label for="txtWorkEmail" class="col-sm-2 col-form-label">Work Email</label>
  <div class="col-sm-10">
    <input type="email" class="form-control" id="txtWorkEmail" placeholder="name@company.com">
  </div>
</div>
```

### Analysis & Resolution:
1. Label text: `"Work Email"`.
2. Inspects `for="txtWorkEmail"`.
3. Verifies `txtWorkEmail` is static and unique.
4. Tier 1 applies (`By.ID`).

### Generated Framework Code:
```python
# Standard Page Object Descriptor
input_work_email = find_by(By.ID, "txtWorkEmail", label="Work Email Input")

# Method Decorator Format
@find_by(By.ID, "txtWorkEmail")
input_work_email = None
```

---

## Example 2: Modern Tailwind / Floating Label (No `for`, No ID)

### Raw HTML:
```html
<div class="relative z-0 w-full mb-5 group">
  <input type="tel" name="primary_phone" id="floating_phone" class="block py-2.5 px-0 w-full text-sm text-gray-900 bg-transparent border-0 border-b-2 border-gray-300 appearance-none focus:outline-none focus:ring-0 peer" placeholder=" " required />
  <label class="peer-focus:font-medium absolute text-sm text-gray-500 duration-300 transform -translate-y-6 scale-75 top-3 -z-10 origin-[0]">Primary Contact Phone</label>
</div>
```

### Analysis & Resolution:
1. Label has no `for` attribute.
2. ID `floating_phone` might be static, but let's check Name: `name="primary_phone"` is clean and unique (Tier 2).
3. If Name was missing, Progressive Container Traversal (Tier 3) finds:
   `//label[normalize-space()='Primary Contact Phone']/preceding-sibling::input` or `/ancestor::div[.//input][1]//input`.

### Generated Framework Code:
```python
# Primary: By.NAME (Tier 2)
input_primary_phone = find_by(By.NAME, "primary_phone", label="Primary Phone Input")

# Resilient Fallback: Semantic Label Traversal (Tier 3)
input_primary_phone_alt = find_by(
    By.XPATH,
    "//label[normalize-space()='Primary Contact Phone']/ancestor::div[.//input][1]//input",
    label="Primary Phone Input"
)
```

---

## Example 3: Nested Input inside Label (Switch / Toggle / Checkbox)

### Raw HTML:
```html
<label class="switch-container">
  <input type="checkbox" name="notifications_opt_in" />
  <span class="slider round"></span>
  Enable Real-Time SMS Notifications
</label>
```

### Analysis & Resolution:
1. Input is a direct child of `<label>`.
2. Normalized label text matches `"Enable Real-Time SMS Notifications"`.
3. Tag type is `checkbox` -> Prefix `chk_`.

### Generated Framework Code:
```python
chk_enable_sms_notifications = find_by(
    By.XPATH,
    "//label[contains(normalize-space(), 'Enable Real-Time SMS Notifications')]//input[@type='checkbox']",
    label="Enable Real-Time SMS Notifications Checkbox"
)

# Method Decorator Format
@find_by(
    By.XPATH,
    "//label[contains(normalize-space(), 'Enable Real-Time SMS Notifications')]//input[@type='checkbox']"
)
chk_enable_sms_notifications = None
```

---

## Example 4: Complex Multi-Input Grid (Upward Container Ascent)

### Raw HTML:
```html
<div class="checkout-section">
  <h3>Shipping Information</h3>
  <div class="grid grid-cols-2 gap-4">
    <div class="field-container">
      <label class="field-title">First Name</label>
      <input type="text" class="input-box" />
    </div>
    <div class="field-container">
      <label class="field-title">Last Name</label>
      <input type="text" class="input-box" />
    </div>
  </div>
</div>
```

### Analysis & Resolution:
1. Both inputs share identical generic class `.input-box`.
2. No IDs or Names exist.
3. Upward container search for `"First Name"`:
   - Level 1: `input.find_parent()` is `<div class="field-container">`.
   - Contains label `"First Name"` and exactly **ONE** input.
   - Stop traversal!

### Generated Framework Code:
```python
input_first_name = find_by(
    By.XPATH,
    "//label[normalize-space()='First Name']/ancestor::div[.//input][1]//input",
    label="First Name Input"
)

input_last_name = find_by(
    By.XPATH,
    "//label[normalize-space()='Last Name']/ancestor::div[.//input][1]//input",
    label="Last Name Input"
)
```

---

## Example 5: Icon Button Without Visible Text

### Raw HTML:
```html
<header class="top-nav">
  <button type="button" aria-label="Open User Profile Menu" class="btn-icon circle-avatar">
    <svg width="24" height="24">...</svg>
  </button>
</header>
```

### Analysis & Resolution:
1. Button has no text child, only an SVG.
2. Has `aria-label="Open User Profile Menu"` (Tier 4).
3. Tag is `button` -> Prefix `btn_`.

### Generated Framework Code:
```python
btn_user_profile_menu = find_by(
    By.CSS_SELECTOR,
    "button[aria-label='Open User Profile Menu']",
    label="User Profile Menu Button"
)

# Method Decorator Format
@find_by(By.CSS_SELECTOR, "button[aria-label='Open User Profile Menu']")
btn_user_profile_menu = None
```

