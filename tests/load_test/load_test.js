// Install k6 `brew install k6`
import http from "k6/http";
import { sleep, check } from "k6";

export const options = {
  vus: 1,
  duration: "5s",
};

export default function () {
  const api_key = "";

  const params = {
    headers: {
      "Content-Type": "application/json",
      "x-api-key": api_key,
    },
  };

  const candidates = Array.from({ length: 1000 }, (_, i) => ({
    product_id: i + Math.floor(Math.random() * 10000),
    opensearch_score: 1000 - i,
  }));

  const payload = JSON.stringify({
    request_id: "test_request_id",
    query: { query: "candle" },
    candidates: candidates,
    user: { user_id: "1234", user_name: "user_name" },
    user_page_size: 10,
    user_page: 20,
    candidate_page_size: 1000,
    candidate_page: 0,
  });

  const r = http.post(
    "https://api.wyvern.ai/api/v1/product-search-ranking",
    payload,
    params
  );
  check(r, { "status was 200": (r) => r.status == 200 });
  console.log(r.body);
  sleep(1);
}
/*
{
    "request_id": "test_request_id",
    "query": {"query": "candle"},
    "candidates": [
        {"product_id": "0", "opensearch_score": 1000},
    ],
    "user": {"user_id": "1234", "user_name": "user_name"},
    "user_page_size": 10,
    "user_page": 20,
    "candidate_page_size": 1000,
    "candidate_page": 0
}
*/
