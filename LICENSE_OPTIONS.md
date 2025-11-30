# Licensing Options for memo-transcriber

**Goal:** Free to use and hack on for anyone, but commercial projects require permission (may be granted free or for a fee).

---

## Quick Comparison Table

| License | Commercial Restriction | Converts to Open Source? | Complexity | OSI Approved? | Best For |
|---------|----------------------|-------------------------|-----------|---------------|----------|
| **PolyForm NC** | ❌ Permanent | No | ⭐ Simple | No | Simple, permanent control |
| **FSL** | ❌ 2 years | ✅ Apache 2.0/MIT (2y) | ⭐⭐ Moderate | No | Eventually fully open |
| **BSL** | ❌ 4 years | ✅ GPL-compatible (4y) | ⭐⭐⭐ Complex | No | Enterprise standard |
| **AGPL + Commercial** | Copyleft (viral) | N/A (already OSI) | ⭐⭐⭐⭐ Very Complex | Yes | Traditional dual licensing |
| **Custom** | Your terms | Your choice | ⭐-⭐⭐⭐⭐ Varies | No | Total control, legal risk |

---

## Option 1: PolyForm NonCommercial 1.0 ⭐ RECOMMENDED

### How it works
- ✅ Free to use, modify, and distribute for **non-commercial purposes**
- ❌ Commercial use requires separate permission/license from you
- 📜 Simple, plain-language license created by lawyers specifically for software
- ♾️ Permanent restriction (doesn't auto-convert to open source)

### Official License
- **URL:** https://polyformproject.org/licenses/noncommercial/1.0.0/
- **GitHub:** https://github.com/polyformproject/polyform-licenses
- **SPDX Identifier:** PolyForm-Noncommercial-1.0.0

### Real-World Projects Using This
- **EPPlus** - Excel library (switched from LGPL to PolyForm NC in v5)
- **Umbrel** - Personal server OS
- **Enable Data Union** - Educational data analytics platform

### Pros
- ✅ Dead simple to understand and apply
- ✅ Clear commercial restriction with no ambiguity
- ✅ Written by experienced licensing lawyers
- ✅ You control commercial permissions case-by-case
- ✅ Plain English, user-friendly

### Cons
- ❌ Not OSI-approved "open source"
- ❌ Commercial restriction is permanent (no auto-conversion)
- ❌ Less well-known than traditional licenses

### Why This Fits Your Needs
**Perfect match:** "Free for anyone to use and hack on, but commercial requires permission." This is exactly what PolyForm NC does.

---

## Option 2: Functional Source License (FSL)

### How it works
- ✅ Free to use/modify for **non-competing purposes**
- ❌ Competing commercial use prohibited for **2 years**
- 🔄 Automatically converts to **Apache 2.0 or MIT** after 2 years
- 📅 Each version has its own 2-year clock (v1.0 released Jan 2025 → open source Jan 2027)

### Official License
- **Website:** https://fsl.software/
- **Template:** https://fsl.software/FSL-1.1-ALv2.template.md
- **Announcement:** https://blog.sentry.io/introducing-the-functional-source-license-freedom-without-free-riding/

### Real-World Projects Using This
- **Sentry** - Application monitoring platform (creator of FSL)
- **Codecov** - Code coverage tool
- **Convex** - Backend platform

### Pros
- ✅ Eventually becomes truly open source (Apache 2.0/MIT)
- ✅ Modern license gaining adoption
- ✅ Simpler than BSL
- ✅ 2 years is shorter timeline than BSL's 4 years
- ✅ Explicitly designed for SaaS/developer tools

### Cons
- ❌ "Competing use" definition can be fuzzy/disputed
- ❌ Not OSI open source during restriction period
- ❌ Less legal precedent than BSL
- ❌ Lose permanent commercial control after 2 years

---

## Option 3: Business Source License (BSL 1.1)

### How it works
- ✅ Source available, free for **non-production use**
- ❌ Production use restricted (you can grant exceptions via "Additional Use Grant")
- 🔄 Converts to **GPL-compatible license** after **4 years** (or sooner, your choice)
- 📅 Per-version timeline: v1.0 released Jan 2025 → GPL Jan 2029

### Official License
- **MariaDB:** https://mariadb.com/bsl11/
- **HashiCorp:** https://www.hashicorp.com/en/bsl
- **Wikipedia:** https://en.wikipedia.org/wiki/Business_Source_License

### Real-World Projects Using This
- **HashiCorp** - Terraform, Vault, Consul, Nomad, Packer, Vagrant (all switched to BSL in 2023)
- **MariaDB MaxScale** - Database load balancer (creator of BSL in 2013)
- **Couchbase** - NoSQL database
- **CockroachDB** - Distributed SQL database
- **Sentry** (before switching to FSL)

### Pros
- ✅ Well-established (created 2013, widely used)
- ✅ Flexible "Additional Use Grant" clause for exceptions
- ✅ Eventually becomes GPL (true open source)
- ✅ Strong legal precedent
- ✅ Enterprise-recognized

### Cons
- ❌ More complex than FSL/PolyForm
- ❌ 4-year timeline is longer
- ❌ Production vs non-production distinction can be unclear
- ❌ Not OSI open source during restriction period

---

## Option 4: Dual Licensing (AGPL + Commercial)

### How it works
- 📜 Offer under **AGPL** (strong copyleft - forces sharing modifications)
- 💰 Sell separate **commercial licenses** to those who don't want AGPL obligations
- 🔗 AGPL requires sharing source code if software used as a service (SaaS loophole closer)
- 🎯 AGPL is "scary" for businesses → drives them to buy commercial license

### Official License
- **AGPL v3:** https://www.gnu.org/licenses/agpl-3.0.en.html
- **Wikipedia:** https://en.wikipedia.org/wiki/GNU_Affero_General_Public_License

### Real-World Projects Using This
- **MongoDB** - Used AGPL dual licensing until 2018 (switched to SSPL)
- **Odoo** - Business software suite
- **SugarCRM** - Customer relationship management
- **RethinkDB** - Database (historically)
- **HumHub** - Social networking platform
- **WURFL** - Device detection

**Note:** Some projects use AGPL *without* dual licensing:
- **Plausible Analytics** - Web analytics (AGPL only, business model is paid hosting)
- **GitLab CE** - Uses MIT (not AGPL), "open core" model with proprietary EE

### Pros
- ✅ AGPL is OSI-approved open source
- ✅ Proven business model
- ✅ Strong copyleft drives commercial license sales
- ✅ No time limit on commercial control

### Cons
- ❌ Complex for users to understand
- ❌ AGPL is viral/restrictive (can scare away users)
- ❌ Not beginner-friendly
- ❌ Requires dual licensing infrastructure
- ❌ Community may fork and stay AGPL

---

## Option 5: Custom "Source Available" License

### How it works
- 📝 Write your own simple terms
- 📋 Explicitly state: "Free for personal/educational/non-commercial, commercial requires permission"
- ⚖️ Total control over exact wording

### Example Template
```
Copyright (c) [Year] [Your Name]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software for NON-COMMERCIAL purposes, including the rights to use,
copy, modify, merge, publish, and distribute, subject to the following:

COMMERCIAL USE (including but not limited to incorporating this software into
a commercial product or service) REQUIRES explicit written permission from
the copyright holder.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND.
```

### Pros
- ✅ Total control over exact terms
- ✅ Say exactly what you mean
- ✅ No conversion timeline if you don't want one
- ✅ Simple and direct

### Cons
- ❌ No legal precedent
- ❌ May have loopholes you didn't anticipate
- ❌ Not standardized (reduces trust/adoption)
- ❌ Requires legal review to be safe
- ❌ "Commercial use" definition may be unclear

---

## Recommendation

### For memo-transcriber: **PolyForm NonCommercial 1.0** 🎯

**Why this is the best fit:**

1. ✅ **Crystal clear:** Free for anyone to use and hack on
2. ✅ **Simple:** No confusing conversion dates or competing-use definitions
3. ✅ **Flexible:** You control commercial permissions case-by-case
4. ✅ **Professional:** Written by licensing lawyers, legally sound
5. ✅ **Matches your goal:** "I may give it free or charge, that's my choice"
6. ✅ **Low friction:** Users understand "non-commercial" easily

**Alternative if you want eventual open source:**
- **FSL** (2 years) - Modern, cleaner than BSL
- **BSL** (4 years) - More established, enterprise-recognized

---

## Implementation Steps

Once you choose a license:

1. **Add LICENSE file** to repository root
2. **Add SPDX identifier** to `pyproject.toml`:
   ```toml
   [project]
   license = {text = "PolyForm-Noncommercial-1.0.0"}
   # OR for FSL: license = {text = "FSL-1.1-ALv2"}
   # OR for BSL: license = {text = "BUSL-1.1"}
   ```
3. **Update README.md** with license badge and explanation
4. **Add copyright headers** to source files (optional but recommended)
5. **Create COMMERCIAL-LICENSE-REQUEST.md** (template for commercial inquiries)

---

## Questions to Help You Decide

1. **Do you want the code to eventually become fully open source?**
   - Yes → FSL (2y) or BSL (4y)
   - No → PolyForm NC or AGPL dual licensing

2. **How important is OSI "open source" label?**
   - Very → AGPL dual licensing (only OSI option)
   - Not very → Any other option

3. **How complex are you willing to go?**
   - Keep it simple → PolyForm NC
   - Moderate → FSL
   - Complex is fine → BSL or AGPL dual

4. **What's your primary goal?**
   - Prevent commercial exploitation → Any option works
   - Drive commercial license sales → AGPL dual licensing
   - Eventually give to community → FSL or BSL
   - Keep permanent control → PolyForm NC

---

## Resources

- **Choose a License:** https://choosealicense.com/
- **PolyForm Project:** https://polyformproject.org/
- **FSL Website:** https://fsl.software/
- **FOSSA License Guide:** https://fossa.com/blog/
- **TLDRLegal (Plain English):** https://www.tldrlegal.com/

---

**Ready to choose?** Let me know which option you prefer and I'll help implement it!
