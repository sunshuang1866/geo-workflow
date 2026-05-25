#!/bin/bash
cd /home/openeuler/workspace/geo-workflow

QUESTIONS="q_001,q_002,q_003,q_004,q_005,q_006,q_007,q_008,q_009,q_010,q_011,q_012,q_013,q_014,q_015,q_016,q_017,q_018,q_019,q_020,q_021,q_022,q_023,q_024,q_025,q_026,q_027,q_028,q_029,q_030,q_031,q_032,q_033,q_034,q_035,q_036,q_037,q_038,q_039,q_040,q_041,q_042,q_043,q_044,q_045,q_046,q_047,q_048,q_049,q_050,q_051,q_052,q_053,q_054,q_055,q_056,q_057,q_058,q_059,q_060"

echo "=== Starting DeepSeek run at $(date) ===" | tee -a assessments/openUBMC/2026-05-19/run.log

python3 .claude/skills/platform-chat/scripts/run-platform-chat.py \
  --platform deepseek-web \
  --community openUBMC \
  --date 2026-05-19 \
  --questions "$QUESTIONS" \
  --timeout 120 \
  2>&1 | tee -a assessments/openUBMC/2026-05-19/run.log

echo "=== DeepSeek complete at $(date). Starting Qwen... ===" | tee -a assessments/openUBMC/2026-05-19/run.log

python3 .claude/skills/platform-chat/scripts/run-platform-chat.py \
  --platform qwen-web \
  --community openUBMC \
  --date 2026-05-19 \
  --questions "$QUESTIONS" \
  --timeout 120 \
  2>&1 | tee -a assessments/openUBMC/2026-05-19/run.log

echo "=== Both platforms complete at $(date) ===" | tee -a assessments/openUBMC/2026-05-19/run.log
