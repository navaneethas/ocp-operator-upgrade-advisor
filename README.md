# 🚀 OpenShift Operator Upgrade Advisor

**Check operator compatibility before upgrading OpenShift clusters**

I built this tool to help us (and customers) check if their operators are compatible with target OpenShift versions. I noticed many struggle with manual version checking, so this should make it much easier.

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

## 🖥️ Quick Start

**1. Download the CLI tool:**
```bash
curl -O https://raw.githubusercontent.com/navaneethas/ocp-operator-upgrade-advisor/main/cli-analyzer-enhanced.py
curl -O https://raw.githubusercontent.com/navaneethas/ocp-operator-upgrade-advisor/main/compatibility_matrix.json
```

**2. Collect your cluster data:**
```bash
(echo '{"clusterVersion":'; oc get clusterversion version -o json; \
 echo ',"subscriptions":'; oc get sub -A -o json; \
 echo ',"clusterServiceVersions":'; oc get csv -A -o json; \
 echo '}') > cluster-data.json
```

**3. Run analysis:**
```bash
python3 cli-analyzer-enhanced.py cluster-data.json 4.22 compatibility_matrix.json
```

**4. Review results!**

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

**2. Navigate to must-gather:**
```bash
cd /path/to/must-gather
```

**3. Use with geminicli:**
```bash
geminicli check operator compatibility for OCP 4.20
```

**Full guide:** [SUPPORTSHELL-SHARING-GUIDE.md](SUPPORTSHELL-SHARING-GUIDE.md)

---

## ✨ Features

- ✅ **180 Red Hat Operators** - Complete coverage
- ✅ **OCP 4.12 - 4.22** - All recent versions
- ✅ **CLI Tool** - Easy to use command-line interface
- ✅ **Geminicli Integration** - Works in supportshell
- ✅ **No External Dependencies** - Python stdlib only
- ✅ **Color-Coded Results** - Easy to understand
- ✅ **Version Recommendations** - Know what to upgrade to
- ✅ **Build Metadata Handling** - Works with versions like `2.4.0+0.12345`
- ✅ **Catalog Validation** - Detects non-Red Hat operators
- ✅ **Offline Capable** - No internet required for analysis

---

## 🎓 How It Works

1. **Data Collection:** Gather cluster data using `oc` commands
2. **Version Extraction:** Parse operator versions from CSVs
3. **Compatibility Check:** Match against Red Hat operator catalogs (4.12-4.22)
4. **Analysis:** Determine compatibility status and recommendations
5. **Display:** Show results in CLI

**Data Source:** Red Hat operator catalog indexes collected via `oc-mirror`

---

## 💬 Feedback

Have suggestions, found a bug, or want to share how you're using this tool? 

**Submit feedback:** [Open an issue on GitHub](https://github.com/navaneethas/ocp-operator-upgrade-advisor/issues/new)

Let us know:
- 🐛 Bug reports
- 💡 Feature requests
- 📝 Improvement suggestions
- 🎉 Success stories
- 📋 Missing operators or OCP versions

Your feedback helps make this tool better for everyone!
