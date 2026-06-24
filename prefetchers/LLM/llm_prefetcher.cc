#include "llm_prefetcher.h"

#include <array>
#include <cstddef>
#include <cstdint>
#include <iostream>

namespace
{
constexpr std::size_t MAX_PREFETCH_REQUESTS = 8;

struct policy_input {
  champsim::address addr{};
  champsim::address ip{};
  uint8_t cache_hit = 0;
  bool useful_prefetch = false;
  access_type type = access_type::LOAD;
  uint32_t metadata_in = 0;
};

struct policy_request {
  bool valid = false;
  champsim::address addr{};
  bool fill_this_level = true;
  uint32_t metadata = 0;
  uint8_t owner_kind = 0;
  uint8_t issue_family = 0;
  uint8_t issue_degree = 0;
  bool page_max_degree_gt1 = false;
  uint16_t owner_index = 0;
  uint64_t owner_tag = 0;
  int32_t score = 0;
};

struct policy_decision {
  std::array<policy_request, MAX_PREFETCH_REQUESTS> requests{};
  std::size_t count = 0;
  std::size_t candidates = 0;
};

struct stats_type {
  uint64_t triggers = 0;
  uint64_t demand_triggers = 0;
  uint64_t upper_prefetch_triggers = 0;
  uint64_t useful_prefetch_hits = 0;
  uint64_t decisions = 0;
  uint64_t candidates = 0;
  uint64_t prefetch_requests = 0;
  uint64_t prefetch_issued = 0;
  uint64_t no_prefetch_decisions = 0;
};

stats_type& stats()
{
  static stats_type value;
  return value;
}

bool is_demand(access_type type)
{
  return type == access_type::LOAD || type == access_type::RFO;
}

bool is_trigger(access_type type)
{
  return is_demand(type) || type == access_type::PREFETCH;
}

#include "llm_prefetcher_policy.inc"
} // namespace

void llm_prefetcher::prefetcher_initialize()
{
  stats() = {};
  reset_llm_prefetcher_policy();
}

uint32_t llm_prefetcher::prefetcher_cache_operate(champsim::address addr, champsim::address ip, uint8_t cache_hit, bool useful_prefetch, access_type type,
                                                  uint32_t metadata_in)
{
  if (!is_trigger(type))
    return metadata_in;

  auto& s = stats();
  ++s.triggers;
  if (is_demand(type))
    ++s.demand_triggers;
  if (type == access_type::PREFETCH)
    ++s.upper_prefetch_triggers;
  if (useful_prefetch)
    ++s.useful_prefetch_hits;

  const policy_input input{addr, ip, cache_hit, useful_prefetch, type, metadata_in};
  const auto decision = build_llm_prefetcher_policy(input);
  ++s.decisions;
  s.candidates += decision.candidates;
  if (decision.count == 0)
    ++s.no_prefetch_decisions;

  for (std::size_t i = 0; i < decision.count && i < decision.requests.size(); ++i) {
    const auto& request = decision.requests.at(i);
    if (!request.valid)
      continue;
    ++s.prefetch_requests;
    const auto issued = prefetch_line(request.addr, request.fill_this_level, request.metadata);
    if (issued) {
      ++s.prefetch_issued;
      record_llm_prefetcher_issue(request);
    }
  }

  return metadata_in;
}

uint32_t llm_prefetcher::prefetcher_cache_fill(champsim::address addr, long set, long way, uint8_t prefetch, champsim::address evicted_addr, uint32_t metadata_in)
{
  (void)addr;
  (void)set;
  (void)way;
  (void)prefetch;
  observe_llm_prefetcher_eviction(evicted_addr);
  return metadata_in;
}

void llm_prefetcher::prefetcher_final_stats()
{
  const auto s = stats();
  std::cout << "LLM_PREFETCHER iter_044: high_unused_pressure_abstain" << std::endl;
  std::cout << "LLM_PREFETCHER triggers: " << s.triggers << " demand: " << s.demand_triggers
            << " upper_prefetch: " << s.upper_prefetch_triggers << " useful_hits: " << s.useful_prefetch_hits << std::endl;
  std::cout << "LLM_PREFETCHER decisions: " << s.decisions << " candidates: " << s.candidates << " requests: " << s.prefetch_requests
            << " no_prefetch: " << s.no_prefetch_decisions << std::endl;
  std::cout << "LLM_PREFETCHER issued: " << s.prefetch_issued << std::endl;
  print_llm_prefetcher_policy_stats();
}
