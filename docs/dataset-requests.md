# 데이터셋 담당에게 보내는 요청 (헤드 → 사용자 전달)

기준: 학습 서버 `~/taehyeon/data/dataset_10_14`(lora_a/b train·val·test 전수)와 `~/WS/dataset/docs/IO_SPEC.md`. 계약(boundary-contracts v2.0.0-rc1)은 **현재 데이터를 기준으로** 만들었다. 아래는 정리하면 서비스가 단순해지는 항목이다. 데이터가 바뀌면 계약도 바뀌므로, 바꾸기 전에 알려 달라.

확인한 것(boundary-contracts `V2_DRAFT.md`, 데이터 전수 집계):

1. 여기서 "문서"는 학습 서버의 `~/WS/dataset/docs/IO_SPEC.md`(팀 문서)다. 우리가 만든 문서가 아니다. IO_SPEC 표에 없는 `reason` 4종이 데이터에 있다(합 55건, 모두 REASK): OTHER_BEVERAGE 45, MISSING_NUMBER 6, UNPARSED_VALUE 2, INVALID_OPTION 2. 네 가지 모두 정규화기 쪽 문서(`~/minji/openit-normalizer/docs/routing_policy.md` 266~271행, status UNCLEAR)와 코드(`~/minji/normalizer-v0.4.1/normalizer/mappings.py`)에 정의되어 있다(확인, 2026-10-27). 즉 데이터와 정규화기는 맞고 IO_SPEC만 이 4종을 표에 싣지 않았다. IO_SPEC 표에 추가해 달라.
2. `BEVERAGE_MISSING`은 문서에서 HOLD 사유인데 데이터에서는 REASK 44건뿐이다. HOLD는 UNCERTAIN만 있다.
3. CONFIRM의 `next_item`은 333건 중 278건이 현재 문항이 아니라 충돌 대상 칸의 문항이다. 문서는 "현재 문항"이라고 적었다.
4. 술 종류를 모를 때 괄호 없는 키(`Q7_1.amount`, `Q7_1.unit`)가 나온다(`targets`에서 129건). 문서의 예시(`whisky`, `.beverage`)는 데이터와 다르다(데이터는 `spirits`, `glass`).
5. 57행은 NEXT인데 `next_item`이 같은 말에서 일부 칸이 이미 채워진 문항(Q4_1, Q5_1)이라, `next.text`가 이미 받은 내용을 다시 묻게 된다. 작업 기록에도 미해결로 적혀 있다. 남은 칸만 묻는 `next.text`(또는 `ask`)를 주는 방식이 필요하다.
6. CONFLICT_WITH_PREVIOUS 279건의 `ask`가 모두 같은 틀이고 괄호 속 영문이 글자 그대로 들어 있다.
7. Q10 END 건수(185)와 START 건수(110)가 문서(NEXT 70·정정 12·모름 5·거절 5, START 150~200)와 다르다.
8. 정규화 쪽을 다른 담당자가 수정 중이라고 `~/WS/AGENTS.md`에 적혀 있다. 확정 시점과 바뀌는 범위를 알려 달라.

미정(서비스 쪽에서 필요한 것): `ask` 문장 틀 표와 칸 설명표(IO_SPEC 7장). 서비스가 표 찾기로 B 입력을 만들 때 쓴다.
