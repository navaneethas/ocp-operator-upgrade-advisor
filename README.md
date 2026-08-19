# 🚀 OpenShift Operator Upgrade Advisor

**Check operator compatibility before upgrading OpenShift clusters**

I built this skill to help us (and customers) check if their operators are compatible with target OpenShift versions. I noticed many struggle with manual version checking, so this should make it much easier.

Give it a spin and let me know what you think! (created by Claude) 🤖

---

## 🎯 What It Does

Before upgrading your OpenShift cluster, this tool tells you:

- ✅ Which operators are compatible with the target OCP version
- ⚠️ Which operators need upgrades
- ❌ Which operators won't work
- 📊 Recommended versions for each operator
- 🎯 Maximum OCP version each operator supports

**Coverage:** 180 Red Hat operators across OCP 4.12 → 4.22

---

## 🔧 Using in Supportshell (Geminicli)

For Red Hat support engineers working in supportshell:

**1. Download the skill and matrix:**
```bash
curl -o ocp-operator-compatibility.md \
  https://raw.githubusercontent.com/navaneethas/ocp-operator-upgrade-advisor/main/ocp-operator-compatibility.md

curl -o compatibility_matrix.json \
  https://raw.githubusercontent.com/navaneethas/ocp-operator-upgrade-advisor/main/compatibility_matrix.json
```

**2. Use with geminicli:**

**⚠️ Important:** Run the `gemini` command from the same directory where you downloaded the skill and matrix files.

```bash
gemini check operators compatibility for OCP <OCP_version> /path/to/must-gather
```

**Example:**
```bash
gemini check operators compatibility for OCP 4.22 /cases/12345678/must-gather.local.xxx
```

---

## 🎓 How It Works

1. **Data Collection:** Gather cluster data using `omc` commands
2. **Version Extraction:** Parse operator versions from CSVs
3. **Compatibility Check:** Match against Red Hat operator catalogs (4.12-4.22)
4. **Analysis:** Determine compatibility status and recommendations
5. **Display:** Show results in CLI

**Data Source:** Red Hat operator catalog indexes collected via `oc-mirror`

---

## 💬 Feedback

Give it a spin and let me know what you think!

**Submit feedback:** [Google Form](https://docs.google.com/forms/d/e/1FAIpQLSdPpmM164p9J7kSkFB9ph7V5dBgw4McyhwCjPwMJGCLYKYH9g/viewform?usp=publish-editor)
