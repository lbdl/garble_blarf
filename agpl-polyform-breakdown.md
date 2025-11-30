# AGPL vs PolyForm NonCommercial: A Comprehensive Breakdown

**The Key Question:** Both licenses keep source code open, so what's the difference?

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Core Concepts](#core-concepts)
3. [Side-by-Side Comparison](#side-by-side-comparison)
4. [Real-World Usage Scenarios](#real-world-usage-scenarios)
5. [The "Copyleft" vs "Share-Alike" Distinction](#the-copyleft-vs-share-alike-distinction)
6. [When to Choose Which License](#when-to-choose-which-license)
7. [License Compatibility](#license-compatibility)

---

## Executive Summary

### AGPL (GNU Affero General Public License v3)
**Philosophy:** "If you use this code, you must share your changes - even if you only run it as a service."

- ✅ **True copyleft** - OSI-approved open source
- ✅ **Commercial use allowed** (with obligations)
- ✅ **Source code must stay open** (including network use)
- 🎯 **Goal:** Keep software free and prevent proprietary forks
- ⚖️ **Freedom-focused:** Four freedoms (use, study, share, improve)

### PolyForm NonCommercial 1.0
**Philosophy:** "Use this code freely for non-commercial purposes; commercial use requires my permission."

- ⚠️ **Share-alike (NOT copyleft)** - Not OSI-approved
- ❌ **Commercial use prohibited** (without permission)
- ✅ **Source code must stay open** (with same license)
- 🎯 **Goal:** Prevent commercial exploitation while staying open
- 💰 **Control-focused:** Author retains commercial rights

---

## Core Concepts

### What is Copyleft?

**Copyleft** is a licensing approach that grants freedoms while ensuring those freedoms persist:

1. ✅ **Use** - Run the program for any purpose
2. ✅ **Study** - Examine how it works and modify it
3. ✅ **Share** - Distribute copies to help others
4. ✅ **Improve** - Distribute modified versions

**The Copyleft Requirement:** If you distribute the software (modified or not), you must pass along the same freedoms under the same license.

**Critical Point:** Copyleft **allows commercial use** - it just requires sharing modifications.

---

### What is Share-Alike?

**Share-Alike** requires derivatives to use the same license terms:

- ✅ Source code must remain available
- ✅ Same license must be applied
- ⚠️ May include additional restrictions (like non-commercial)

**Key Difference:** Share-alike is a **mechanism**, copyleft is a **philosophy**. All copyleft licenses are share-alike, but not all share-alike licenses are copyleft.

---

### Why PolyForm NC is Share-Alike but NOT Copyleft

PolyForm NonCommercial **removes freedom #1** (use for any purpose):

```
❌ Use for ANY purpose → ✅ Use for NON-COMMERCIAL purposes only
```

**Result:** Because it restricts use, it doesn't qualify as "copyleft" under the Free Software Foundation definition. Copyleft requires granting the four freedoms; PolyForm NC only grants three.

**However:** It IS share-alike because derivatives must use the same license and stay open-source.

---

## Side-by-Side Comparison

| Aspect | AGPL v3 | PolyForm NonCommercial 1.0 |
|--------|---------|---------------------------|
| **Source Code Must Stay Open** | ✅ Yes | ✅ Yes |
| **Can Close-Source Derivatives** | ❌ No | ❌ No |
| **License Terms Carry Forward** | ✅ Yes (must use AGPL) | ✅ Yes (must use PolyForm NC) |
| **Commercial Use** | ✅ Allowed (with obligations) | ❌ Prohibited (requires permission) |
| **Network Use Triggers Sharing** | ✅ Yes (even SaaS) | ⚠️ Yes (if distributed) |
| **OSI "Open Source" Approved** | ✅ Yes | ❌ No |
| **FSF "Free Software" Approved** | ✅ Yes | ❌ No |
| **Classification** | Strong copyleft | Proprietary share-alike |
| **Freedom Count** | All 4 freedoms | 3 of 4 freedoms |
| **Can Fork and Compete** | ✅ Yes (if share changes) | ❌ Not commercially |
| **Can Use in Proprietary Software** | ❌ No | ❌ No |
| **Can Sell Software** | ✅ Yes (with source) | ❌ No |
| **Can Offer as Paid SaaS** | ✅ Yes (must share code) | ❌ No |
| **Can Use Internally in Company** | ✅ Yes | ⚠️ Only if non-commercial org |
| **Contributor Rights** | Equal (GPL'd forever) | Limited (can't commercialize) |

---

## Real-World Usage Scenarios

### Scenario 1: Individual Developer Making Modifications

**Context:** Alice modifies the code for her personal project.

| Action | AGPL | PolyForm NC |
|--------|------|-------------|
| Modify for personal use | ✅ Allowed, no sharing required | ✅ Allowed, no sharing required |
| Modify and keep private | ✅ Allowed if not distributed | ✅ Allowed if not distributed |
| Modify and share on GitHub | ✅ Must share source (AGPL) | ✅ Must share source (PolyForm NC) |
| Modify and sell on GitHub | ✅ Allowed, must share source | ❌ Prohibited (commercial) |

**Key Difference:** Alice can sell AGPL software (with source), but NOT PolyForm NC software.

---

### Scenario 2: Startup Building a Product

**Context:** TechStartup Inc. wants to use the code in their product.

#### With AGPL:

```
✅ ALLOWED (with obligations):
- Use in commercial product
- Charge customers money
- Build a business around it
- Offer as paid SaaS

⚠️ REQUIRED:
- Share all modifications (even for SaaS)
- License entire product under AGPL
- Provide source to users/customers
- Cannot combine with proprietary code

💡 TYPICAL OUTCOME:
→ Startup pays for commercial dual-license
→ OR builds on different stack
→ OR embraces AGPL and open-sources everything
```

#### With PolyForm NC:

```
❌ PROHIBITED:
- Any commercial use
- Charging customers
- Building a business around it
- Offering as paid service

✅ ALTERNATIVE:
- Contact you for commercial license
- You decide: grant free or charge
- Negotiate custom terms

💡 TYPICAL OUTCOME:
→ Startup contacts copyright holder
→ Negotiates commercial license
→ Pays licensing fee (if required)
```

---

### Scenario 3: Cloud Provider Offering Service

**Context:** BigCloud Corp wants to offer your software as a managed service.

#### With AGPL:

```
✅ ALLOWED:
- Offer as paid cloud service
- Charge customers for hosting
- Make money from support/SLAs

⚠️ REQUIRED (AGPL's special provision):
- Share ALL source code (including modifications)
- Even if they don't distribute software
- Network access = "distribution"
- Must provide download link to users

🎯 WHY AGPL EXISTS:
The "SaaS loophole" - companies would:
1. Take GPL code
2. Modify it heavily
3. Run as service (no "distribution")
4. Never share improvements
AGPL closes this loophole.

💰 BUSINESS IMPACT:
→ Most cloud providers avoid AGPL
→ OR negotiate commercial license
→ OR contribute back to community
```

#### With PolyForm NC:

```
❌ COMPLETELY PROHIBITED:
- Cannot offer as service (commercial use)
- Must contact you for permission
- No "comply and use" option

✅ YOU CONTROL:
- Whether they can use it
- What they pay
- Terms of use

💰 BUSINESS IMPACT:
→ Cloud provider MUST contact you
→ No "just comply" option like AGPL
→ You have full veto power
```

**Key Difference:** AGPL allows commercial competition (with source sharing); PolyForm NC blocks it entirely.

---

### Scenario 4: Open Source Project Fork

**Context:** Developer community wants to fork and improve the project.

#### With AGPL:

```
✅ ENCOURAGED:
- Anyone can fork
- Anyone can improve
- Anyone can distribute
- Even competing projects allowed

📋 REQUIREMENTS:
- Keep AGPL license
- Share all changes
- Maintain four freedoms

🌍 COMMUNITY IMPACT:
- Vibrant ecosystem possible
- Multiple implementations
- Innovation through competition
- Example: MariaDB forked from MySQL

⚠️ RISK FOR ORIGINAL AUTHOR:
- Can't control forks
- Competitors can use your code
- Can't monetize exclusively
```

#### With PolyForm NC:

```
✅ ALLOWED (limited):
- Can fork for personal use
- Can fork for education/research
- Can improve non-commercially
- Can contribute back

❌ BLOCKED:
- Cannot fork and compete commercially
- Cannot build business on fork
- Cannot offer fork as paid service

🌍 COMMUNITY IMPACT:
- Limited commercial ecosystem
- Fewer competing implementations
- Community contributions possible
- But commercial innovation blocked

✅ BENEFIT FOR ORIGINAL AUTHOR:
- You retain commercial monopoly
- Forks can't compete in market
- Still get community improvements
```

**Key Difference:** AGPL enables competitive forks; PolyForm NC prevents commercial competition while allowing contribution.

---

### Scenario 5: Large Enterprise Internal Use

**Context:** MegaCorp Inc wants to use the code internally (not customer-facing).

#### With AGPL:

```
✅ COMPLETELY ALLOWED:
- Use internally without restrictions
- No need to share modifications
- Can customize extensively
- As long as not "distributed"

⚠️ "DISTRIBUTION" TRIGGERS:
- Giving copies to customers
- Offering as service to external users
- Spinning off as separate company

✅ INTERNAL USE = SAFE:
- 10,000 employees using it? Fine.
- Custom modifications? Fine.
- Internal APIs/services? Fine.

💡 ENTERPRISE REALITY:
Most enterprises still avoid AGPL because:
- Risk of accidental distribution
- Complex compliance requirements
- Legal department concerns
```

#### With PolyForm NC:

```
⚠️ DEPENDS ON ORGANIZATION TYPE:

✅ NON-COMMERCIAL ORGS:
- Educational institutions
- Government agencies
- Non-profits
- Research organizations
→ Can use freely

❌ COMMERCIAL COMPANIES:
- For-profit corporations
- Even internal use is "commercial"
- License defines: "make money from use"

📋 POLYFORM NC TEXT:
"Use for commercial purposes means use in
supporting or contributing to a commercial
organization's operations."

❌ MEGACORP VERDICT:
Cannot use at all, even internally,
because MegaCorp is a commercial entity.
```

**Key Difference:** AGPL allows internal use by anyone; PolyForm NC blocks use by commercial entities entirely.

---

### Scenario 6: Educational/Research Use

**Context:** University wants to use code for teaching or research.

#### With AGPL:

```
✅ FULLY ALLOWED:
- Teaching courses
- Research projects
- Student modifications
- Academic papers
- Lab experiments

📋 REQUIREMENTS:
- Share if distribute to students
- Keep AGPL if share publicly
- Normal copyleft rules apply

🎓 COMMON PRACTICE:
Universities often prefer AGPL because:
- Aligns with academic values
- Encourages open research
- Students learn open source
```

#### With PolyForm NC:

```
✅ EXPLICITLY ALLOWED:
- Educational institutions exempt
- Research organizations exempt
- No restrictions for academia

📋 POLYFORM NC TEXT:
"Use by any charitable organization,
educational institution, public research
organization... is use for a permitted
purpose regardless of the source of funding."

🎓 EVEN BETTER FOR EDUCATION:
- Simpler license to explain
- No copyleft complexities
- Students can't commercialize without learning
- Teaches licensing ethics
```

**Key Difference:** Both allow education/research freely; PolyForm NC explicitly exempts these use cases.

---

### Scenario 7: Contributing Back to Project

**Context:** Developer wants to contribute improvements to original project.

#### With AGPL:

```
✅ STRAIGHTFORWARD:
1. Fork the repo
2. Make changes
3. Submit pull request
4. Your code becomes AGPL

⚖️ YOUR RIGHTS:
- You keep copyright (unless CLA)
- Your code is AGPL forever
- Can't revoke license later
- Can use in your own AGPL projects

📋 CONTRIBUTOR EXPERIENCE:
- Clear licensing
- Equal rights with original author
- Part of open source ecosystem
- No permission needed to contribute

🤝 COMMUNITY STANDARD:
Standard open source workflow
```

#### With PolyForm NC:

```
⚠️ COMPLEX SITUATION:
1. Fork the repo
2. Make changes (non-commercial)
3. Submit pull request
4. Your code becomes PolyForm NC

⚖️ YOUR RIGHTS (LIMITED):
- You keep copyright
- But can't commercialize
- Original author controls commercial use
- Asymmetric relationship

📋 CONTRIBUTOR EXPERIENCE:
- You give improvements for free
- Original author can commercialize
- You cannot commercialize
- Potential resentment

⚠️ COMMUNITY CONCERN:
"Why should I contribute if only
the original author can profit?"

💡 TYPICAL SOLUTION:
Require CLA (Contributor License Agreement)
giving original author rights to
relicense contributions.
```

**Key Difference:** AGPL creates equal contributor rights; PolyForm NC creates asymmetry favoring original author.

---

## The "Copyleft" vs "Share-Alike" Distinction

### Why This Matters

The distinction isn't just academic - it has real legal and philosophical implications.

---

### The Four Freedoms (Free Software Foundation)

For software to be "copyleft", it must grant these freedoms:

```
Freedom 0: Use for ANY purpose
Freedom 1: Study how it works
Freedom 2: Redistribute copies
Freedom 3: Distribute modified versions
```

**AGPL:** ✅✅✅✅ (All four)
**PolyForm NC:** ❌✅✅✅ (Only three - fails on "any purpose")

---

### Visual Comparison

```
┌─────────────────────────────────────────────────────────┐
│                    LICENSE SPECTRUM                      │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  Permissive         Copyleft         Share-Alike        │
│  (MIT/Apache)       (AGPL/GPL)       (PolyForm NC)      │
│       │                 │                  │            │
│       ▼                 ▼                  ▼            │
│                                                          │
│  Can close-source   Must stay open    Must stay open   │
│  ✅ Commercial      ✅ Commercial      ❌ Commercial     │
│  ❌ Source req'd    ✅ Source req'd    ✅ Source req'd   │
│  ❌ Share-alike     ✅ Share-alike     ✅ Share-alike    │
│  ❌ Copyleft        ✅ Copyleft        ❌ Copyleft       │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

### Philosophical Differences

#### AGPL Philosophy: "Freedom Over Control"

```
Core Belief: Software should be free for everyone.

Values:
- User freedom paramount
- Community over individual
- Collaboration encouraged
- Commercial use allowed
- Competition welcomed

Mechanism:
- Viral copyleft (spreads freedom)
- Share-alike (preserves freedom)
- Network clause (closes SaaS loophole)

Result:
✅ Vibrant ecosystem
✅ Commercial sustainability possible
⚠️ Original author loses exclusive control
```

#### PolyForm NC Philosophy: "Control Over Freedom"

```
Core Belief: Author should control commercial use.

Values:
- Author's rights paramount
- Individual over community
- Contribution welcome (limited)
- Commercial use restricted
- Competition blocked

Mechanism:
- Non-commercial restriction
- Share-alike (preserves openness)
- Permission-based commercial use

Result:
✅ Author retains commercial monopoly
⚠️ Limited commercial ecosystem
⚠️ Contributor asymmetry
```

---

### Legal Status

#### AGPL

```
✅ OSI-Approved Open Source License
✅ FSF-Approved Free Software License
✅ Debian Free Software Guidelines compliant
✅ Used in Fedora, Ubuntu, etc.
✅ Well-understood by legal departments
✅ Extensive case law and precedent
✅ Compatible with other GPL licenses
```

#### PolyForm NC

```
❌ NOT OSI-Approved Open Source
❌ NOT FSF-Approved Free Software
❌ NOT DFSG compliant
❌ Cannot be in Debian/Fedora main repos
⚠️ Less legal precedent
⚠️ Corporate legal departments wary
❌ Incompatible with open source licenses
✅ Clear terms (lawyer-written)
✅ Gaining adoption in commercial OSS
```

---

## When to Choose Which License

### Choose AGPL When:

✅ **You believe in open source philosophy**
- Four freedoms for all users
- Community over individual profit
- Collaboration and competition welcome

✅ **You want maximum adoption**
- Enterprises can use internally
- Cloud providers can offer (with sharing)
- Vibrant ecosystem possible

✅ **You're okay with commercial competition**
- Competitors must share improvements
- Network effect benefits everyone
- MongoDB, Plausible Analytics model

✅ **You want contributor equality**
- Same rights for everyone
- No asymmetry
- Healthy community possible

✅ **You have alternative revenue**
- Dual licensing (AGPL + commercial)
- Managed hosting/support
- Enterprise features
- Professional services

🎯 **AGPL Sweet Spot:** Developer tools, databases, infrastructure software where community contribution is valuable and dual-licensing model works.

**Examples:** MongoDB (historically), Plausible Analytics, Grafana (some components)

---

### Choose PolyForm NC When:

✅ **You want commercial control**
- Block competitors completely
- Negotiate individual licenses
- Retain exclusive commercial rights

✅ **You're building a commercial product**
- Open core model
- Free for personal use
- Paid commercial licenses
- No "comply and compete" option

✅ **You want simplicity**
- Clear non-commercial restriction
- No viral copyleft complexity
- Easy to explain to users

✅ **Your software is end-user focused**
- Not infrastructure/tools
- Specific problem solution
- Limited community contribution expected

✅ **You're a small team/solo developer**
- Can't compete with cloud giants
- Need protection from exploitation
- Want to monetize directly

🎯 **PolyForm NC Sweet Spot:** End-user applications, specialized tools, solo developer projects where commercial protection is priority over ecosystem growth.

**Examples:** EPPlus (Excel library), Umbrel (personal server)

---

### Decision Framework

```
START HERE: What's your primary goal?

┌─────────────────────────────────────────────────┐
│ Goal: Maximum community adoption & contribution │
│ Revenue: Dual licensing / Services / Hosting    │
│ Okay with: Commercial competition               │
└──────────────────┬──────────────────────────────┘
                   │
                   ▼
               USE AGPL
                   │
    ┌──────────────┴──────────────┐
    │                             │
    ▼                             ▼
Offer Commercial            Or Pure AGPL
Dual License               (Like Plausible)


┌─────────────────────────────────────────────────┐
│ Goal: Protect commercial market position        │
│ Revenue: Direct commercial licenses             │
│ Okay with: Limited ecosystem                    │
└──────────────────┬─────────────────────────────┘
                   │
                   ▼
           USE POLYFORM NC
                   │
                   ▼
        Grant commercial licenses
        on case-by-case basis
```

---

## License Compatibility

### AGPL Compatibility

```
✅ Can combine with:
- AGPL v3 code
- GPL v3 code (becomes AGPL)
- LGPL v3 libraries (limited)

❌ Cannot combine with:
- MIT/Apache (entire work becomes AGPL)
- BSD (entire work becomes AGPL)
- Proprietary code
- PolyForm NC code

⚠️ One-way compatibility:
- Can upgrade GPL → AGPL
- Cannot downgrade AGPL → GPL
```

### PolyForm NC Compatibility

```
⚠️ VERY LIMITED:
- PolyForm NC code only
- Maybe public domain
- Custom negotiation needed

❌ Incompatible with:
- All OSI open source licenses
- AGPL/GPL/MIT/Apache/BSD
- Other copyleft licenses
- Most permissive licenses

💡 Reason:
PolyForm NC is more restrictive than
any OSI license, so combining would
violate the other license's terms.
```

---

## Summary: Quick Reference

| Question | AGPL | PolyForm NC |
|----------|------|-------------|
| **Can I use it for free?** | ✅ Yes | ✅ Yes (non-commercial) |
| **Can I modify it?** | ✅ Yes | ✅ Yes |
| **Can I distribute it?** | ✅ Yes (with source) | ✅ Yes (with source) |
| **Can I close-source my changes?** | ❌ No | ❌ No |
| **Can I sell it?** | ✅ Yes (with source) | ❌ No |
| **Can I offer as paid SaaS?** | ✅ Yes (must share code) | ❌ No |
| **Can I use in my company?** | ✅ Yes (internal use OK) | ⚠️ Only if non-profit |
| **Can I fork and compete?** | ✅ Yes (must share) | ❌ Not commercially |
| **Can I contribute?** | ✅ Yes (equal rights) | ⚠️ Yes (author profits) |
| **Is it "open source"?** | ✅ Yes (OSI-approved) | ❌ No (source-available) |
| **Is it copyleft?** | ✅ Yes (strong) | ❌ No (share-alike only) |

---

## Final Thoughts

### Both licenses keep source code open, but they serve different goals:

**AGPL** = "Keep it free for everyone, including commercial use"
- Philosophy: Freedom
- Community: Encouraged
- Business model: Dual licensing or services
- Control: Shared with community

**PolyForm NC** = "Keep it free for non-commercial; I control commercial"
- Philosophy: Control
- Community: Limited
- Business model: Direct licensing
- Control: Retained by author

### Neither is "better" - they're tools for different objectives.

Choose based on your values, business model, and community goals.

---

## Additional Resources

### AGPL Resources
- **Official License:** https://www.gnu.org/licenses/agpl-3.0.en.html
- **FSF Guide:** https://www.fsf.org/bulletin/2021/fall/the-fundamentals-of-the-agplv3
- **Plain English:** https://www.tldrlegal.com/license/gnu-affero-general-public-license-v3-agpl-3-0
- **Case Studies:** MongoDB, Plausible Analytics, Grafana

### PolyForm NC Resources
- **Official License:** https://polyformproject.org/licenses/noncommercial/1.0.0/
- **GitHub Repo:** https://github.com/polyformproject/polyform-licenses
- **Plain English:** https://www.tldrlegal.com/license/polyform-noncommercial-1-0-0
- **Case Studies:** EPPlus, Umbrel, Enable Data Union

### Licensing Guides
- **Choose a License:** https://choosealicense.com/
- **FOSSA Blog:** https://fossa.com/blog/
- **OSI Licenses:** https://opensource.org/licenses/

---

*This document is for educational purposes and does not constitute legal advice. Consult with a qualified attorney for licensing decisions.*
