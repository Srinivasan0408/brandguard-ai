# AUTOMATED TEST EXECUTION REPORT
## BrandGuard AI — Team: TECHSPARKZ
### Test Suite: `backend/tests/test_brandguard.py`
### Test Runner: Pytest 9.1.1 &bull; Python 3.14.0

---

## 1. Test Execution Summary

| Total Scenarios Tested | Passed | Failed | Skipped | Pass Rate | Execution Time |
|---|---|---|---|---|---|
| **12** | **12** | **0** | **0** | **100.0%** | **2.79s** |

---

## 2. Detailed Scenario Results

| Test ID | Test Name / Scenario | Requirement | Expected Result | Actual Outcome | Status |
|---|---|---|---|---|---|
| **TEST 1** | `test_1_prohibited_term_detected` | Section 18 #1 | A post containing "cheap" flags a terminology finding with high severity. | Finding returned with excerpt "cheap", category "terminology", severity "high", and suggested correction "cost-effective". | **PASSED** |
| **TEST 2** | `test_2_approved_price_mismatch` | Section 18 #2 | Approved price is ₹4,999, but content says ₹5,999. Contradiction returned. | Critical finding returned with detected price "₹5,999", approved value "₹4,999", and source citation. | **PASSED** |
| **TEST 3** | `test_3_promotional_claim_warning` | Section 18 #3 | Content contains "100% guaranteed results". | High-severity claim warning returned citing policy against unsupported guarantees. | **PASSED** |
| **TEST 4** | `test_4_compliant_content_no_false_violations` | Section 18 #4 | Content follows all rules (NovaTech Pro, ₹4,999, disclaimers included). | Zero critical or high-severity violations generated. Clean verification. | **PASSED** |
| **TEST 5** | `test_5_edit_content_and_rerun_review` | Section 18 #5 | User edits content and reruns review. | New revision (Rev #2) snapshot created and review findings reflect edited text. | **PASSED** |
| **TEST 6** | `test_6_submit_for_review_changes_status` | Section 18 #6 | Creator submits draft for review. | Status transitions from `draft` &rarr; `in_review`. Audit event recorded. | **PASSED** |
| **TEST 7** | `test_7_reviewer_requests_changes` | Section 18 #7 | Reviewer requests changes with comments. | Status changes to `changes_requested` and reviewer feedback comment is persisted. | **PASSED** |
| **TEST 8** | `test_8_revisions_preserved_and_inspectable` | Section 18 #8 | Creator submits revised version. | Both Rev #1 and Rev #2 snapshots are preserved and retrievable via API. | **PASSED** |
| **TEST 9** | `test_9_reviewer_approves_revised_content` | Section 18 #9 | Reviewer approves revised content. | Final status becomes `approved` and approval event is written to the audit log. | **PASSED** |
| **TEST 10** | `test_10_unauthorised_user_rejected_from_approval` | Section 18 #10 | Creator role attempts to approve content. | Request is rejected with HTTP 403 Forbidden. RBAC policy enforced. | **PASSED** |
| **TEST 11** | `test_11_file_upload_validation_rejected_safely` | Section 18 #11 | File has unsupported extension (.exe). | Upload safely rejected with HTTP 400 and clear error message. Valid .txt accepted. | **PASSED** |
| **TEST 12** | `test_12_no_llm_key_deterministic_fallback_and_mode_indication` | Section 18 #12 | System runs without external LLM API key. | Engine operates deterministically and health endpoint reports analysis mode. | **PASSED** |

---

## 3. Actual Command Line Output

```text
============================= test session starts =============================
platform win32 -- Python 3.14.0, pytest-9.1.1, pluggy-1.7.0 -- C:\Python314\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\srini\OneDrive\Documents\Brand govern
plugins: anyio-4.14.2, asyncio-1.4.0
asyncio: mode=Mode.STRICT, debug=False
collecting ... collected 12 items

backend/tests/test_brandguard.py::test_1_prohibited_term_detected PASSED [  8%]
backend/tests/test_brandguard.py::test_2_approved_price_mismatch PASSED  [ 16%]
backend/tests/test_brandguard.py::test_3_promotional_claim_warning PASSED [ 25%]
backend/tests/test_brandguard.py::test_4_compliant_content_no_false_violations PASSED [ 33%]
backend/tests/test_brandguard.py::test_5_edit_content_and_rerun_review PASSED [ 41%]
backend/tests/test_brandguard.py::test_6_submit_for_review_changes_status PASSED [ 50%]
backend/tests/test_brandguard.py::test_7_reviewer_requests_changes PASSED [ 58%]
backend/tests/test_brandguard.py::test_8_revisions_preserved_and_inspectable PASSED [ 66%]
backend/tests/test_brandguard.py::test_9_reviewer_approves_revised_content PASSED [ 75%]
backend/tests/test_brandguard.py::test_10_unauthorised_user_rejected_from_approval PASSED [ 83%]
backend/tests/test_brandguard.py::test_11_file_upload_validation_rejected_safely PASSED [ 91%]
backend/tests/test_brandguard.py::test_12_no_llm_key_deterministic_fallback_and_mode_indication PASSED [100%]

======================== 12 passed, 1 warning in 2.79s ========================
```
