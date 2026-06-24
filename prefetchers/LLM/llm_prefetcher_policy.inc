// Included from llm_prefetcher.cc inside an anonymous namespace.
// Iteration 044: high-unused pressure abstain on top of page-churn gated
// upper D7/D8 same-page policy. The table
// semantics and byte budget are documented in
// llm_iterations/iter_044/design/DESIGN.md.

constexpr std::size_t PAGE_STREAM_ENTRIES = 384;
constexpr std::size_t IP_STRIDE_ENTRIES = 384;
constexpr std::size_t ISSUED_LINE_ENTRIES = 512;
constexpr bool UPPER_D78_LOG_ENABLED = false;
constexpr uint8_t INVALID_OFFSET = 0xff;
constexpr int8_t MIN_USEFUL_SCORE = -4;
constexpr int8_t MAX_USEFUL_SCORE = 7;
constexpr uint8_t MAX_CONFIDENCE = 3;
constexpr int64_t MAX_TRACKED_STRIDE = 512;
constexpr uint64_t PAGE_CHURN_MIN_LOOKUPS = 8192;
constexpr uint64_t IP_CHURN_MIN_LOOKUPS = 8192;
constexpr uint64_t GLOBAL_ABSTAIN_MIN_LOOKUPS = 1024;
constexpr uint64_t UPPER_DEPTH_MIN_TRIGGERS = 8192;
constexpr uint64_t GLOBAL_WASTE_MIN_REPLACEMENTS = 65536;
constexpr uint64_t GLOBAL_WASTE_MIN_USED_REPLACEMENTS = 8192;
constexpr std::size_t ISSUE_DEGREE_BUCKETS = 5;
constexpr uint8_t ISSUE_META_FAMILY_MASK = 0x3;
constexpr uint8_t ISSUE_META_DEGREE_MASK = 0x1c;
constexpr uint8_t ISSUE_META_DEGREE_SHIFT = 2;
constexpr uint8_t ISSUE_META_PAGE_MAX_DEGREE_GT1 = 0x20;

enum policy_owner_kind : uint8_t {
  OWNER_NONE = 0,
  OWNER_PAGE_STREAM = 1,
  OWNER_IP_STRIDE = 2,
};

enum issue_family_kind : uint8_t {
  ISSUE_NONE = 0,
  ISSUE_UPPER_PAGE = 1,
  ISSUE_OTHER_PAGE = 2,
  ISSUE_IP = 3,
};

struct page_stream_entry {
  uint64_t tag = 0;
  uint64_t touch_mask = 0;
  uint8_t last_offset = INVALID_OFFSET;
  int8_t last_dir = 0;
  uint8_t dir_conf = 0;
  int8_t useful_score = 0;
  bool valid = false;
};

struct ip_stride_entry {
  uint64_t tag = 0;
  uint64_t last_line = 0;
  int16_t last_stride = 0;
  uint8_t stride_conf = 0;
  int8_t useful_score = 0;
  bool valid = false;
  bool has_last_line = false;
};

struct issued_line_entry {
  uint64_t line_tag = 0;
  uint64_t owner_tag = 0;
  uint16_t owner_index = 0;
  uint16_t issue_epoch = 0;
  uint8_t owner_kind = OWNER_NONE;
  uint8_t issue_meta = 0;
  bool used = false;
  bool valid = false;
};

struct churn_gate_block {
  uint64_t page_lookups = 0;
  uint64_t page_replacements = 0;
  uint64_t page_conf_replacements = 0;
  uint64_t page_positive_replacements = 0;
  uint64_t page_gate_eligible_checks = 0;
  uint64_t page_gate_suppressed_decisions = 0;
  uint64_t ip_lookups = 0;
  uint64_t ip_replacements = 0;
  uint64_t ip_conf_replacements = 0;
  uint64_t ip_positive_replacements = 0;
  uint64_t ip_abstain_eligible_checks = 0;
  uint64_t ip_abstain_suppressed_decisions = 0;
  uint64_t demand_trigger_count = 0;
  uint64_t upper_prefetch_trigger_count = 0;
  uint64_t upper_depth_eligible_checks = 0;
  uint64_t upper_depth_boosted_decisions = 0;
  uint64_t upper_depth_churn_capped_decisions = 0;
  uint64_t candidate_same_line_suppressed = 0;
  uint64_t candidate_off_page_suppressed = 0;
  uint64_t candidate_issued_duplicate_suppressed = 0;
  uint64_t candidate_issued_duplicate_suppressed_used = 0;
  uint64_t candidate_issued_duplicate_suppressed_unused = 0;
  uint64_t candidate_issued_duplicate_suppressed_upper_page = 0;
  uint64_t candidate_issued_duplicate_suppressed_other_page = 0;
  uint64_t candidate_issued_duplicate_suppressed_ip = 0;
  uint64_t candidate_decision_duplicate_suppressed = 0;
  uint64_t issue_epoch = 0;
  uint64_t issued_line_replacements = 0;
  uint64_t issued_line_replacements_used = 0;
  uint64_t issued_line_replacements_unused = 0;
  uint64_t issued_line_same_line_reissues = 0;
  std::array<uint64_t, 4> useful_feedback_age_buckets{};
  std::array<uint64_t, 4> unused_feedback_age_buckets{};
  std::array<uint64_t, 4> used_replacement_age_buckets{};
  std::array<uint64_t, 4> unused_replacement_age_buckets{};
  uint64_t stale_owner_feedback_drops = 0;
  uint64_t useful_feedback_events = 0;
  uint64_t unused_feedback_events = 0;
  uint64_t global_abstain_eligible_checks = 0;
  uint64_t global_abstain_suppressed_decisions = 0;
  uint64_t global_abstain_first_ip_lookups = 0;
  uint64_t global_abstain_first_ip_replacements = 0;
  uint64_t global_abstain_first_page_lookups = 0;
  uint64_t global_abstain_first_page_replacements = 0;
  uint64_t global_waste_eligible_checks = 0;
  uint64_t global_waste_suppressed_decisions = 0;
  uint64_t global_waste_first_issue_replacements = 0;
  uint64_t global_waste_first_unused_replacements = 0;
  uint64_t global_waste_first_used_replacements = 0;
  uint64_t global_waste_first_page_lookups = 0;
  uint64_t global_waste_first_page_replacements = 0;
  uint64_t replay_decision_id = 0;
  uint64_t sample_page_tag = 0;
  uint64_t sample_page_touch_mask = 0;
  uint16_t sample_page_index = 0;
  uint8_t sample_page_last_offset = INVALID_OFFSET;
  int8_t sample_page_last_dir = 0;
  uint8_t sample_page_dir_conf = 0;
  int8_t sample_page_useful_score = 0;
  bool sample_page_valid = false;
  uint64_t sample_ip_tag = 0;
  uint64_t sample_ip_last_line = 0;
  uint64_t sample_ip_update_line = 0;
  uint16_t sample_ip_index = 0;
  int16_t sample_ip_last_stride = 0;
  uint8_t sample_ip_stride_conf = 0;
  int8_t sample_ip_useful_score = 0;
  bool sample_ip_valid = false;
  bool sample_ip_has_last_line = false;
  uint64_t sample_issued_line_tag = 0;
  uint64_t sample_issued_owner_tag = 0;
  uint16_t sample_issued_index = 0;
  uint16_t sample_issued_owner_index = 0;
  uint16_t sample_issued_epoch = 0;
  uint8_t sample_issued_owner_kind = OWNER_NONE;
  uint8_t sample_issued_issue_meta = 0;
  uint8_t sample_issued_family = ISSUE_NONE;
  uint8_t sample_issued_degree = 0;
  bool sample_issued_page_max_degree_gt1 = false;
  bool sample_issued_used = false;
  bool sample_issued_valid = false;
};

static_assert(sizeof(page_stream_entry) == 24);
static_assert(sizeof(ip_stride_entry) == 24);
static_assert(sizeof(issued_line_entry) == 24);
static_assert(sizeof(churn_gate_block) == 600);

using page_stream_table_type = std::array<page_stream_entry, PAGE_STREAM_ENTRIES>;
using ip_stride_table_type = std::array<ip_stride_entry, IP_STRIDE_ENTRIES>;
using issued_line_table_type = std::array<issued_line_entry, ISSUED_LINE_ENTRIES>;

inline page_stream_table_type& page_stream_table()
{
  static page_stream_table_type table{};
  return table;
}

inline ip_stride_table_type& ip_stride_table()
{
  static ip_stride_table_type table{};
  return table;
}

inline issued_line_table_type& issued_line_table()
{
  static issued_line_table_type table{};
  return table;
}

inline churn_gate_block& churn_gate()
{
  static churn_gate_block gate{};
  return gate;
}

inline uint64_t line_tag(champsim::address addr)
{
  return addr.to<uint64_t>() >> LOG2_BLOCK_SIZE;
}

inline uint64_t page_tag(champsim::address addr)
{
  return addr.to<uint64_t>() >> LOG2_PAGE_SIZE;
}

inline uint8_t page_offset(champsim::address addr)
{
  return static_cast<uint8_t>(line_tag(addr) & 63u);
}

inline uint64_t offset_bit(uint8_t offset)
{
  return uint64_t{1} << offset;
}

inline uint16_t page_stream_index(uint64_t page)
{
  return static_cast<uint16_t>(page % PAGE_STREAM_ENTRIES);
}

inline uint16_t ip_stride_index(uint64_t ip)
{
  return static_cast<uint16_t>((ip ^ (ip >> 17) ^ (ip >> 33)) % IP_STRIDE_ENTRIES);
}

inline uint16_t issued_line_index(uint64_t line)
{
  return static_cast<uint16_t>(line % ISSUED_LINE_ENTRIES);
}

inline int access_type_code(access_type type)
{
  return static_cast<int>(type);
}

inline void log_upper_d78_access(const policy_input& input, uint64_t line, uint64_t page, uint8_t offset)
{
  if (!UPPER_D78_LOG_ENABLED)
    return;

  std::cout << "LLM_PREFETCHER_D78 A " << churn_gate().replay_decision_id << ' ' << line << ' ' << page << ' ' << static_cast<unsigned>(offset) << ' '
            << access_type_code(input.type) << ' ' << static_cast<unsigned>(input.cache_hit) << ' ' << input.useful_prefetch << '\n';
}

inline void log_upper_d78_probe(int64_t candidate_line, uint64_t current_line, uint64_t page, uint8_t offset, int degree, int dir, int32_t score,
                                uint8_t predicted_conf, const char* availability)
{
  if (!UPPER_D78_LOG_ENABLED)
    return;

  std::cout << "LLM_PREFETCHER_D78 Y " << churn_gate().replay_decision_id << ' ' << candidate_line << ' ' << current_line << ' ' << page << ' '
            << static_cast<unsigned>(offset) << ' ' << degree << ' ' << dir << ' ' << score << ' ' << static_cast<unsigned>(predicted_conf) << ' '
            << availability << '\n';
}

inline bool issued_line_valid(const issued_line_entry& row)
{
  return row.valid;
}

inline bool issued_line_used(const issued_line_entry& row)
{
  return row.used;
}

inline void mark_issued_line_used(issued_line_entry& row)
{
  row.used = true;
}

inline uint8_t normalized_issue_family(uint8_t family)
{
  if (family == ISSUE_UPPER_PAGE || family == ISSUE_OTHER_PAGE || family == ISSUE_IP)
    return family;

  return ISSUE_NONE;
}

inline uint8_t normalized_issue_degree(uint8_t degree)
{
  if (degree >= ISSUE_DEGREE_BUCKETS)
    return static_cast<uint8_t>(ISSUE_DEGREE_BUCKETS - 1);

  return degree;
}

inline uint8_t pack_issue_meta(uint8_t family, uint8_t degree, bool page_max_degree_gt1)
{
  auto meta = static_cast<uint8_t>(normalized_issue_family(family) | (normalized_issue_degree(degree) << ISSUE_META_DEGREE_SHIFT));
  if (page_max_degree_gt1)
    meta |= ISSUE_META_PAGE_MAX_DEGREE_GT1;
  return meta;
}

inline uint8_t issue_meta_family(uint8_t meta)
{
  return normalized_issue_family(meta & ISSUE_META_FAMILY_MASK);
}

inline uint8_t issue_meta_degree(uint8_t meta)
{
  return normalized_issue_degree((meta & ISSUE_META_DEGREE_MASK) >> ISSUE_META_DEGREE_SHIFT);
}

inline bool issue_meta_page_max_degree_gt1(uint8_t meta)
{
  return (meta & ISSUE_META_PAGE_MAX_DEGREE_GT1) != 0;
}

inline uint16_t issued_row_age(const issued_line_entry& row)
{
  return static_cast<uint16_t>(static_cast<uint16_t>(churn_gate().issue_epoch) - row.issue_epoch);
}

inline std::size_t age_bucket_index(uint16_t age)
{
  if (age <= 8)
    return 0;
  if (age <= 64)
    return 1;
  if (age <= 512)
    return 2;
  return 3;
}

inline void record_age_bucket(std::array<uint64_t, 4>& buckets, uint16_t age)
{
  ++buckets.at(age_bucket_index(age));
}

inline void record_page_stream_sample(uint16_t index, const page_stream_entry& row)
{
  auto& gate = churn_gate();
  if (gate.sample_page_valid && row.dir_conf < gate.sample_page_dir_conf && row.useful_score <= gate.sample_page_useful_score)
    return;

  gate.sample_page_tag = row.tag;
  gate.sample_page_touch_mask = row.touch_mask;
  gate.sample_page_index = index;
  gate.sample_page_last_offset = row.last_offset;
  gate.sample_page_last_dir = row.last_dir;
  gate.sample_page_dir_conf = row.dir_conf;
  gate.sample_page_useful_score = row.useful_score;
  gate.sample_page_valid = row.valid;
}

inline void record_ip_stride_sample(uint16_t index, const ip_stride_entry& row, uint64_t update_line)
{
  if (!row.valid || !row.has_last_line || row.last_stride == 0)
    return;

  auto& gate = churn_gate();
  if (gate.sample_ip_valid && row.stride_conf < gate.sample_ip_stride_conf && row.useful_score <= gate.sample_ip_useful_score)
    return;

  gate.sample_ip_tag = row.tag;
  gate.sample_ip_last_line = row.last_line;
  gate.sample_ip_update_line = update_line;
  gate.sample_ip_index = index;
  gate.sample_ip_last_stride = row.last_stride;
  gate.sample_ip_stride_conf = row.stride_conf;
  gate.sample_ip_useful_score = row.useful_score;
  gate.sample_ip_valid = row.valid;
  gate.sample_ip_has_last_line = row.has_last_line;
}

inline void record_issued_line_sample(uint16_t index, const issued_line_entry& row)
{
  auto& gate = churn_gate();
  if (gate.sample_issued_valid && issue_meta_family(row.issue_meta) != ISSUE_UPPER_PAGE)
    return;

  gate.sample_issued_line_tag = row.line_tag;
  gate.sample_issued_owner_tag = row.owner_tag;
  gate.sample_issued_index = index;
  gate.sample_issued_owner_index = row.owner_index;
  gate.sample_issued_epoch = row.issue_epoch;
  gate.sample_issued_owner_kind = row.owner_kind;
  gate.sample_issued_issue_meta = row.issue_meta;
  gate.sample_issued_family = issue_meta_family(row.issue_meta);
  gate.sample_issued_degree = issue_meta_degree(row.issue_meta);
  gate.sample_issued_page_max_degree_gt1 = issue_meta_page_max_degree_gt1(row.issue_meta);
  gate.sample_issued_used = row.used;
  gate.sample_issued_valid = row.valid;
}

inline int8_t clamp_useful_score(int value)
{
  if (value < MIN_USEFUL_SCORE)
    return MIN_USEFUL_SCORE;
  if (value > MAX_USEFUL_SCORE)
    return MAX_USEFUL_SCORE;
  return static_cast<int8_t>(value);
}

inline uint8_t bump_confidence(uint8_t value)
{
  return value < MAX_CONFIDENCE ? static_cast<uint8_t>(value + 1) : MAX_CONFIDENCE;
}

inline int bounded_degree(int32_t score, int high_score_cap = 2)
{
  if (score >= 3)
    return high_score_cap;
  return 1;
}

inline bool real_demand_ip(const policy_input& input)
{
  return is_demand(input.type) && input.ip.to<uint64_t>() != 0;
}

inline int direction_from_delta(int delta)
{
  if (delta > 0)
    return 1;
  if (delta < 0)
    return -1;
  return 0;
}

inline bool same_page_line(uint64_t page, uint64_t line)
{
  return (line >> (LOG2_PAGE_SIZE - LOG2_BLOCK_SIZE)) == page;
}

inline void record_page_owner_collision(const page_stream_entry& victim)
{
  auto& gate = churn_gate();
  ++gate.page_replacements;
  if (victim.dir_conf > 0)
    ++gate.page_conf_replacements;
  if (victim.useful_score > 0)
    ++gate.page_positive_replacements;
}

inline page_stream_entry& lookup_page_stream(uint64_t page)
{
  auto& gate = churn_gate();
  ++gate.page_lookups;

  const auto index = page_stream_index(page);
  auto& row = page_stream_table().at(index);
  if (!row.valid || row.tag != page) {
    if (row.valid)
      record_page_owner_collision(row);
    row = {};
    row.valid = true;
    row.tag = page;
    row.last_offset = INVALID_OFFSET;
  }
  return row;
}

inline ip_stride_entry& lookup_ip_stride(uint64_t ip)
{
  auto& gate = churn_gate();
  ++gate.ip_lookups;

  const auto index = ip_stride_index(ip);
  auto& row = ip_stride_table().at(index);
  if (!row.valid || row.tag != ip) {
    if (row.valid) {
      ++gate.ip_replacements;
      if (row.stride_conf > 0)
        ++gate.ip_conf_replacements;
      if (row.useful_score > 0)
        ++gate.ip_positive_replacements;
    }
    row = {};
    row.valid = true;
    row.tag = ip;
  }
  return row;
}

inline issued_line_entry* find_issued_line(uint64_t line)
{
  auto& row = issued_line_table().at(issued_line_index(line));
  if (issued_line_valid(row) && row.line_tag == line)
    return &row;

  return nullptr;
}

inline bool try_adjust_owner_score(const issued_line_entry& issued, int delta)
{
  if (issued.owner_kind == OWNER_PAGE_STREAM && issued.owner_index < PAGE_STREAM_ENTRIES) {
    auto& owner = page_stream_table().at(issued.owner_index);
    if (owner.valid && owner.tag == issued.owner_tag) {
      owner.useful_score = clamp_useful_score(owner.useful_score + delta);
      return true;
    }
    return false;
  }

  if (issued.owner_kind == OWNER_IP_STRIDE && issued.owner_index < IP_STRIDE_ENTRIES) {
    auto& owner = ip_stride_table().at(issued.owner_index);
    if (owner.valid && owner.tag == issued.owner_tag) {
      owner.useful_score = clamp_useful_score(owner.useful_score + delta);
      return true;
    }
  }

  return false;
}

inline bool adjust_owner_score(const issued_line_entry& issued, int delta)
{
  return try_adjust_owner_score(issued, delta);
}

inline void apply_useful_feedback(uint64_t line)
{
  auto* issued = find_issued_line(line);
  if (issued == nullptr || issued_line_used(*issued))
    return;

  auto& gate = churn_gate();
  const auto age = issued_row_age(*issued);
  record_age_bucket(gate.useful_feedback_age_buckets, age);
  mark_issued_line_used(*issued);
  if (adjust_owner_score(*issued, 1))
    ++gate.useful_feedback_events;
  else
    ++gate.stale_owner_feedback_drops;
}

inline bool duplicate_in_decision(const policy_decision& decision, champsim::address addr)
{
  const auto line = line_tag(addr);
  for (std::size_t index = 0; index < decision.count; ++index) {
    if (line_tag(decision.requests.at(index).addr) == line)
      return true;
  }
  return false;
}

inline void record_duplicate_suppression_family(churn_gate_block& gate, uint8_t family)
{
  switch (normalized_issue_family(family)) {
  case ISSUE_UPPER_PAGE:
    ++gate.candidate_issued_duplicate_suppressed_upper_page;
    break;
  case ISSUE_OTHER_PAGE:
    ++gate.candidate_issued_duplicate_suppressed_other_page;
    break;
  case ISSUE_IP:
    ++gate.candidate_issued_duplicate_suppressed_ip;
    break;
  default:
    break;
  }
}

inline bool candidate_available(const policy_decision& decision, uint64_t current_line, uint64_t page, uint64_t candidate_line, bool allow_cross_page)
{
  auto& gate = churn_gate();
  if (candidate_line == current_line) {
    ++gate.candidate_same_line_suppressed;
    return false;
  }
  if (!allow_cross_page && !same_page_line(page, candidate_line)) {
    ++gate.candidate_off_page_suppressed;
    return false;
  }
  if (auto* issued = find_issued_line(candidate_line); issued != nullptr) {
    const auto issued_family = issue_meta_family(issued->issue_meta);
    const auto age = issued_row_age(*issued);
    ++gate.candidate_issued_duplicate_suppressed;
    if (issued_line_used(*issued))
      ++gate.candidate_issued_duplicate_suppressed_used;
    else
      ++gate.candidate_issued_duplicate_suppressed_unused;
    record_duplicate_suppression_family(gate, issued_family);
    return false;
  }

  const auto candidate_addr = champsim::address{candidate_line << LOG2_BLOCK_SIZE};
  if (duplicate_in_decision(decision, candidate_addr)) {
    ++gate.candidate_decision_duplicate_suppressed;
    return false;
  }
  return true;
}

inline const char* classify_probe_availability(const policy_decision& decision, uint64_t page, int64_t candidate_line_signed)
{
  if (candidate_line_signed < 0)
    return "negative_line";

  const auto candidate_line = static_cast<uint64_t>(candidate_line_signed);
  if (!same_page_line(page, candidate_line))
    return "off_page";

  if (find_issued_line(candidate_line) != nullptr)
    return "issued_duplicate";

  const auto candidate_addr = champsim::address{candidate_line << LOG2_BLOCK_SIZE};
  if (duplicate_in_decision(decision, candidate_addr))
    return "decision_duplicate";

  return "same_page_available";
}

inline std::size_t effective_request_limit(uint8_t request_family, std::size_t backing_limit)
{
  if (request_family == ISSUE_UPPER_PAGE)
    return backing_limit;

  return 4;
}

inline void add_candidate(policy_decision& decision, const policy_input& input, uint64_t current_line, uint64_t page, uint8_t offset, uint64_t candidate_line,
                          uint8_t owner_kind, uint8_t issue_family, uint8_t issue_degree, bool page_max_degree_gt1, uint16_t owner_index,
                          uint64_t owner_tag, int32_t score, bool allow_cross_page = false)
{
  (void)input;
  (void)offset;
  ++decision.candidates;
  const auto request_family = normalized_issue_family(issue_family);
  const auto request_degree = normalized_issue_degree(issue_degree);

  if (decision.count >= effective_request_limit(request_family, decision.requests.size()))
    return;
  if (!candidate_available(decision, current_line, page, candidate_line, allow_cross_page))
    return;

  auto& request = decision.requests.at(decision.count++);
  request.valid = true;
  request.addr = champsim::address{candidate_line << LOG2_BLOCK_SIZE};
  request.fill_this_level = true;
  request.metadata = 0;
  request.owner_kind = owner_kind;
  request.issue_family = request_family;
  request.issue_degree = request_degree;
  request.page_max_degree_gt1 = page_max_degree_gt1;
  request.owner_index = owner_index;
  request.owner_tag = owner_tag;
  request.score = score;
}

inline void add_page_stream_candidates(policy_decision& decision, const policy_input& input, const page_stream_entry& page_row, uint64_t current_line,
                                       uint64_t page, uint8_t offset, int high_score_degree_cap)
{
  if (page_row.last_offset == INVALID_OFFSET || page_row.last_offset == offset)
    return;

  const auto dir = direction_from_delta(static_cast<int>(offset) - static_cast<int>(page_row.last_offset));
  if (dir == 0 || page_row.last_dir != dir)
    return;

  const auto predicted_conf = bump_confidence(page_row.dir_conf);
  const auto upper_bonus = input.type == access_type::PREFETCH ? 1 : 0;
  const auto score = static_cast<int32_t>(predicted_conf) + page_row.useful_score + upper_bonus;
  if (predicted_conf < 1 || score < 1)
    return;

  const auto page_index = page_stream_index(page);
  const auto page_base_line = page << (LOG2_PAGE_SIZE - LOG2_BLOCK_SIZE);
  const auto family = input.type == access_type::PREFETCH && high_score_degree_cap > 2 ? ISSUE_UPPER_PAGE : ISSUE_OTHER_PAGE;
  const auto max_degree = bounded_degree(score, high_score_degree_cap);
  const auto page_max_degree_gt1 = max_degree >= 2;
  for (int degree = 1; degree <= max_degree; ++degree) {
    const auto candidate_offset = static_cast<int>(offset) + dir * degree;
    if (candidate_offset < 0 || candidate_offset >= 64)
      break;
    add_candidate(decision, input, current_line, page, offset, page_base_line + static_cast<uint64_t>(candidate_offset), OWNER_PAGE_STREAM, family,
                  static_cast<uint8_t>(degree), page_max_degree_gt1, page_index, page, score);
  }

  if (UPPER_D78_LOG_ENABLED && family == ISSUE_UPPER_PAGE && max_degree == 6) {
    for (int degree = 7; degree <= 8; ++degree) {
      const auto candidate_line_signed = static_cast<int64_t>(current_line) + static_cast<int64_t>(dir) * degree;
      log_upper_d78_probe(candidate_line_signed, current_line, page, offset, degree, dir, score, predicted_conf,
                          classify_probe_availability(decision, page, candidate_line_signed));
    }
  }
}

inline void add_ip_stride_candidates(policy_decision& decision, const policy_input& input, const ip_stride_entry& ip_row, uint64_t current_line, uint64_t page,
                                     uint8_t offset, uint64_t ip)
{
  if (!ip_row.valid || !ip_row.has_last_line || ip_row.last_line == current_line)
    return;

  const auto stride64 = static_cast<int64_t>(current_line) - static_cast<int64_t>(ip_row.last_line);
  if (stride64 == 0 || stride64 < -MAX_TRACKED_STRIDE || stride64 > MAX_TRACKED_STRIDE)
    return;
  if (stride64 != ip_row.last_stride)
    return;

  const auto predicted_conf = bump_confidence(ip_row.stride_conf);
  const auto score = static_cast<int32_t>(predicted_conf) + ip_row.useful_score;
  if (predicted_conf < 1 || score < 1)
    return;

  const auto ip_index = ip_stride_index(ip);
  for (int degree = 1; degree <= bounded_degree(score, 3); ++degree) {
    const auto candidate_line_signed = static_cast<int64_t>(current_line) + stride64 * degree;
    if (candidate_line_signed < 0)
      break;
    add_candidate(decision, input, current_line, page, offset, static_cast<uint64_t>(candidate_line_signed), OWNER_IP_STRIDE, ISSUE_IP,
                  static_cast<uint8_t>(degree), false, ip_index, ip, score);
  }
}

inline void update_page_stream(page_stream_entry& page_row, uint8_t offset)
{
  page_row.touch_mask |= offset_bit(offset);

  if (page_row.last_offset != INVALID_OFFSET && page_row.last_offset != offset) {
    const auto dir = direction_from_delta(static_cast<int>(offset) - static_cast<int>(page_row.last_offset));
    if (dir != 0) {
      page_row.dir_conf = page_row.last_dir == dir ? bump_confidence(page_row.dir_conf) : 0;
      page_row.last_dir = static_cast<int8_t>(dir);
    }
  }

  page_row.last_offset = offset;
}

inline void update_ip_stride(ip_stride_entry& ip_row, uint64_t current_line)
{
  if (ip_row.has_last_line && ip_row.last_line != current_line) {
    const auto stride64 = static_cast<int64_t>(current_line) - static_cast<int64_t>(ip_row.last_line);
    if (stride64 >= -MAX_TRACKED_STRIDE && stride64 <= MAX_TRACKED_STRIDE) {
      const auto stride = static_cast<int16_t>(stride64);
      ip_row.stride_conf = ip_row.last_stride == stride ? bump_confidence(ip_row.stride_conf) : 0;
      ip_row.last_stride = stride;
    } else {
      ip_row.stride_conf = 0;
      ip_row.last_stride = 0;
    }
  }

  ip_row.last_line = current_line;
  ip_row.has_last_line = true;
  record_ip_stride_sample(ip_stride_index(ip_row.tag), ip_row, current_line);
}

inline void reset_llm_prefetcher_policy()
{
  page_stream_table() = {};
  ip_stride_table() = {};
  issued_line_table() = {};
  churn_gate() = {};
}

inline void record_llm_prefetcher_issue(const policy_request& request)
{
  const auto line = line_tag(request.addr);
  auto& row = issued_line_table().at(issued_line_index(line));
  auto& gate = churn_gate();
  ++gate.issue_epoch;
  if (issued_line_valid(row)) {
    const auto old_age = issued_row_age(row);
    ++gate.issued_line_replacements;
    if (issued_line_used(row)) {
      ++gate.issued_line_replacements_used;
      record_age_bucket(gate.used_replacement_age_buckets, old_age);
    } else {
      ++gate.issued_line_replacements_unused;
      record_age_bucket(gate.unused_replacement_age_buckets, old_age);
    }
    if (row.line_tag == line)
      ++gate.issued_line_same_line_reissues;
  }
  row = {};
  row.line_tag = line;
  row.owner_kind = request.owner_kind;
  row.issue_meta = pack_issue_meta(request.issue_family, request.issue_degree, request.page_max_degree_gt1);
  row.owner_index = request.owner_index;
  row.owner_tag = request.owner_tag;
  row.issue_epoch = static_cast<uint16_t>(gate.issue_epoch);
  row.used = false;
  row.valid = true;
  record_issued_line_sample(issued_line_index(line), row);
}

inline void observe_llm_prefetcher_eviction(champsim::address evicted_addr)
{
  if (evicted_addr.to<uint64_t>() == 0)
    return;

  const auto line = line_tag(evicted_addr);
  auto* row = find_issued_line(line);
  if (row == nullptr)
    return;

  if (!issued_line_used(*row)) {
    record_age_bucket(churn_gate().unused_feedback_age_buckets, issued_row_age(*row));
    if (adjust_owner_score(*row, -1))
      ++churn_gate().unused_feedback_events;
    else
      ++churn_gate().stale_owner_feedback_drops;
  }
  *row = {};
}

inline bool page_churn_gate_active();
inline bool ip_churn_abstain_active();
inline bool global_high_churn_abstain_active();
inline bool global_high_unused_pressure_abstain_active();
inline int page_high_score_degree_cap(const policy_input& input);

inline policy_decision build_llm_prefetcher_policy(const policy_input& input)
{
  policy_decision decision{};
  if (!is_trigger(input.type))
    return decision;

  const auto line = line_tag(input.addr);
  const auto page = page_tag(input.addr);
  const auto offset = page_offset(input.addr);
  const auto ip = input.ip.to<uint64_t>();

  auto& gate = churn_gate();
  ++gate.replay_decision_id;
  log_upper_d78_access(input, line, page, offset);

  if (input.useful_prefetch)
    apply_useful_feedback(line);

  if (is_demand(input.type))
    ++gate.demand_trigger_count;
  if (input.type == access_type::PREFETCH)
    ++gate.upper_prefetch_trigger_count;

  auto& page_row = lookup_page_stream(page);
  const auto global_high_churn_abstain = global_high_churn_abstain_active();
  const auto global_waste_abstain = global_high_unused_pressure_abstain_active();
  const auto global_abstain = global_high_churn_abstain || global_waste_abstain;
  const auto abstain = ip_churn_abstain_active();

  if (global_abstain)
    ++churn_gate().global_abstain_suppressed_decisions;
  if (global_waste_abstain)
    ++churn_gate().global_waste_suppressed_decisions;
  if (abstain)
    ++churn_gate().ip_abstain_suppressed_decisions;
  if (!global_abstain && !abstain) {
    if (page_churn_gate_active())
      ++churn_gate().page_gate_suppressed_decisions;
    else
      add_page_stream_candidates(decision, input, page_row, line, page, offset, page_high_score_degree_cap(input));
  }
  if (real_demand_ip(input)) {
    auto& ip_row = lookup_ip_stride(ip);
    if (!global_abstain && !abstain)
      add_ip_stride_candidates(decision, input, ip_row, line, page, offset, ip);
    update_ip_stride(ip_row, line);
  }

  update_page_stream(page_row, offset);
  record_page_stream_sample(page_stream_index(page), page_row);

  return decision;
}

inline bool page_churn_gate_active()
{
  auto& gate = churn_gate();
  if (gate.page_lookups < PAGE_CHURN_MIN_LOOKUPS)
    return false;

  ++gate.page_gate_eligible_checks;
  return gate.page_replacements * 8 >= gate.page_lookups;
}

inline bool ip_churn_abstain_active()
{
  auto& gate = churn_gate();
  if (gate.ip_lookups < IP_CHURN_MIN_LOOKUPS)
    return false;

  ++gate.ip_abstain_eligible_checks;
  return gate.ip_replacements * 8 >= gate.ip_lookups;
}

inline bool global_high_churn_abstain_active()
{
  auto& gate = churn_gate();
  if (gate.ip_lookups < GLOBAL_ABSTAIN_MIN_LOOKUPS || gate.page_lookups < GLOBAL_ABSTAIN_MIN_LOOKUPS)
    return false;

  ++gate.global_abstain_eligible_checks;
  const auto high_ip_churn = gate.ip_replacements * 4 >= gate.ip_lookups;
  const auto high_page_churn = gate.page_replacements * 8 >= gate.page_lookups;
  if (!high_ip_churn || !high_page_churn)
    return false;

  if (gate.global_abstain_first_ip_lookups == 0) {
    gate.global_abstain_first_ip_lookups = gate.ip_lookups;
    gate.global_abstain_first_ip_replacements = gate.ip_replacements;
    gate.global_abstain_first_page_lookups = gate.page_lookups;
    gate.global_abstain_first_page_replacements = gate.page_replacements;
  }
  return true;
}

inline bool global_high_unused_pressure_abstain_active()
{
  auto& gate = churn_gate();
  const auto used = gate.issued_line_replacements_used;
  const auto unused = gate.issued_line_replacements_unused;
  const auto replacements = used + unused;
  if (replacements < GLOBAL_WASTE_MIN_REPLACEMENTS || used < GLOBAL_WASTE_MIN_USED_REPLACEMENTS || gate.page_lookups < PAGE_CHURN_MIN_LOOKUPS)
    return false;

  ++gate.global_waste_eligible_checks;
  if (gate.page_replacements * 64 <= gate.page_lookups)
    return false;
  if (gate.page_replacements * 8 >= gate.page_lookups)
    return false;
  if (unused <= 2 * used)
    return false;

  if (gate.global_waste_first_issue_replacements == 0) {
    gate.global_waste_first_issue_replacements = replacements;
    gate.global_waste_first_unused_replacements = unused;
    gate.global_waste_first_used_replacements = used;
    gate.global_waste_first_page_lookups = gate.page_lookups;
    gate.global_waste_first_page_replacements = gate.page_replacements;
  }
  return true;
}

inline int page_high_score_degree_cap(const policy_input& input)
{
  if (input.type != access_type::PREFETCH)
    return 2;

  auto& gate = churn_gate();
  if (gate.demand_trigger_count + gate.upper_prefetch_trigger_count < UPPER_DEPTH_MIN_TRIGGERS)
    return 2;

  ++gate.upper_depth_eligible_checks;
  if (gate.upper_prefetch_trigger_count >= 4 * gate.demand_trigger_count) {
    ++gate.upper_depth_boosted_decisions;
    if (gate.page_lookups >= PAGE_CHURN_MIN_LOOKUPS && gate.page_replacements * 64 > gate.page_lookups) {
      ++gate.upper_depth_churn_capped_decisions;
      return 6;
    }
    return 8;
  }

  return 2;
}

inline double ratio(uint64_t numerator, uint64_t denominator)
{
  if (denominator == 0)
    return 0.0;
  return static_cast<double>(numerator) / static_cast<double>(denominator);
}

inline void print_llm_prefetcher_policy_stats()
{
  const auto gate = churn_gate();
  std::cout << "LLM_PREFETCHER churn_gate:"
            << " page_lookups: " << gate.page_lookups
            << " page_replacements: " << gate.page_replacements
            << " page_replacements_per_lookup: " << ratio(gate.page_replacements, gate.page_lookups)
            << " page_conf_replacements: " << gate.page_conf_replacements
            << " page_positive_replacements: " << gate.page_positive_replacements
            << " page_gate_eligible_checks: " << gate.page_gate_eligible_checks
            << " page_gate_suppressed_decisions: " << gate.page_gate_suppressed_decisions
            << " page_gate_suppressed_per_eligible: " << ratio(gate.page_gate_suppressed_decisions, gate.page_gate_eligible_checks)
            << " ip_lookups: " << gate.ip_lookups
            << " ip_replacements: " << gate.ip_replacements
            << " ip_replacements_per_lookup: " << ratio(gate.ip_replacements, gate.ip_lookups)
            << " ip_conf_replacements: " << gate.ip_conf_replacements
            << " ip_positive_replacements: " << gate.ip_positive_replacements
            << " ip_abstain_eligible_checks: " << gate.ip_abstain_eligible_checks
            << " ip_abstain_suppressed_decisions: " << gate.ip_abstain_suppressed_decisions
            << " ip_abstain_suppressed_per_eligible: " << ratio(gate.ip_abstain_suppressed_decisions, gate.ip_abstain_eligible_checks)
            << " demand_trigger_count: " << gate.demand_trigger_count
            << " upper_prefetch_trigger_count: " << gate.upper_prefetch_trigger_count
            << " upper_depth_eligible_checks: " << gate.upper_depth_eligible_checks
            << " upper_depth_boosted_decisions: " << gate.upper_depth_boosted_decisions
            << " upper_depth_churn_capped_decisions: " << gate.upper_depth_churn_capped_decisions
            << " upper_depth_boosted_per_eligible: " << ratio(gate.upper_depth_boosted_decisions, gate.upper_depth_eligible_checks)
            << " upper_depth_churn_capped_per_boosted: " << ratio(gate.upper_depth_churn_capped_decisions, gate.upper_depth_boosted_decisions)
            << " candidate_same_line_suppressed: " << gate.candidate_same_line_suppressed
            << " candidate_off_page_suppressed: " << gate.candidate_off_page_suppressed
            << " candidate_issued_duplicate_suppressed: " << gate.candidate_issued_duplicate_suppressed
            << " candidate_issued_duplicate_suppressed_used: " << gate.candidate_issued_duplicate_suppressed_used
            << " candidate_issued_duplicate_suppressed_unused: " << gate.candidate_issued_duplicate_suppressed_unused
            << " candidate_issued_duplicate_suppressed_upper_page: " << gate.candidate_issued_duplicate_suppressed_upper_page
            << " candidate_issued_duplicate_suppressed_other_page: " << gate.candidate_issued_duplicate_suppressed_other_page
            << " candidate_issued_duplicate_suppressed_ip: " << gate.candidate_issued_duplicate_suppressed_ip
            << " candidate_decision_duplicate_suppressed: " << gate.candidate_decision_duplicate_suppressed
            << " issue_epoch: " << gate.issue_epoch
            << " issued_line_replacements: " << gate.issued_line_replacements
            << " issued_line_replacements_used: " << gate.issued_line_replacements_used
            << " issued_line_replacements_unused: " << gate.issued_line_replacements_unused
            << " issued_line_same_line_reissues: " << gate.issued_line_same_line_reissues
            << " useful_feedback_age_le8: " << gate.useful_feedback_age_buckets.at(0)
            << " useful_feedback_age_le64: " << gate.useful_feedback_age_buckets.at(1)
            << " useful_feedback_age_le512: " << gate.useful_feedback_age_buckets.at(2)
            << " useful_feedback_age_gt512: " << gate.useful_feedback_age_buckets.at(3)
            << " unused_feedback_age_le8: " << gate.unused_feedback_age_buckets.at(0)
            << " unused_feedback_age_le64: " << gate.unused_feedback_age_buckets.at(1)
            << " unused_feedback_age_le512: " << gate.unused_feedback_age_buckets.at(2)
            << " unused_feedback_age_gt512: " << gate.unused_feedback_age_buckets.at(3)
            << " used_replacement_age_le8: " << gate.used_replacement_age_buckets.at(0)
            << " used_replacement_age_le64: " << gate.used_replacement_age_buckets.at(1)
            << " used_replacement_age_le512: " << gate.used_replacement_age_buckets.at(2)
            << " used_replacement_age_gt512: " << gate.used_replacement_age_buckets.at(3)
            << " unused_replacement_age_le8: " << gate.unused_replacement_age_buckets.at(0)
            << " unused_replacement_age_le64: " << gate.unused_replacement_age_buckets.at(1)
            << " unused_replacement_age_le512: " << gate.unused_replacement_age_buckets.at(2)
            << " unused_replacement_age_gt512: " << gate.unused_replacement_age_buckets.at(3)
            << " stale_owner_feedback_drops: " << gate.stale_owner_feedback_drops
            << " useful_feedback_events: " << gate.useful_feedback_events
            << " unused_feedback_events: " << gate.unused_feedback_events
            << " global_abstain_eligible_checks: " << gate.global_abstain_eligible_checks
            << " global_abstain_suppressed_decisions: " << gate.global_abstain_suppressed_decisions
            << " global_abstain_first_ip_lookups: " << gate.global_abstain_first_ip_lookups
            << " global_abstain_first_ip_replacements: " << gate.global_abstain_first_ip_replacements
            << " global_abstain_first_page_lookups: " << gate.global_abstain_first_page_lookups
            << " global_abstain_first_page_replacements: " << gate.global_abstain_first_page_replacements
            << " global_waste_eligible_checks: " << gate.global_waste_eligible_checks
            << " global_waste_suppressed_decisions: " << gate.global_waste_suppressed_decisions
            << " global_waste_first_issue_replacements: " << gate.global_waste_first_issue_replacements
            << " global_waste_first_unused_replacements: " << gate.global_waste_first_unused_replacements
            << " global_waste_first_used_replacements: " << gate.global_waste_first_used_replacements
            << " global_waste_first_page_lookups: " << gate.global_waste_first_page_lookups
            << " global_waste_first_page_replacements: " << gate.global_waste_first_page_replacements << std::endl;
  std::cout << "LLM_PREFETCHER sample_page_stream:"
            << " valid: " << gate.sample_page_valid
            << " index: " << gate.sample_page_index
            << " tag: " << gate.sample_page_tag
            << " touch_mask: " << gate.sample_page_touch_mask
            << " last_offset: " << static_cast<int>(gate.sample_page_last_offset)
            << " last_dir: " << static_cast<int>(gate.sample_page_last_dir)
            << " dir_conf: " << static_cast<int>(gate.sample_page_dir_conf)
            << " useful_score: " << static_cast<int>(gate.sample_page_useful_score) << std::endl;
  std::cout << "LLM_PREFETCHER sample_ip_stride:"
            << " valid: " << gate.sample_ip_valid
            << " has_last_line: " << gate.sample_ip_has_last_line
            << " index: " << gate.sample_ip_index
            << " tag: " << gate.sample_ip_tag
            << " last_line: " << gate.sample_ip_last_line
            << " update_line: " << gate.sample_ip_update_line
            << " last_stride: " << gate.sample_ip_last_stride
            << " stride_conf: " << static_cast<int>(gate.sample_ip_stride_conf)
            << " useful_score: " << static_cast<int>(gate.sample_ip_useful_score) << std::endl;
  std::cout << "LLM_PREFETCHER sample_issued_line:"
            << " valid: " << gate.sample_issued_valid
            << " used: " << gate.sample_issued_used
            << " index: " << gate.sample_issued_index
            << " line_tag: " << gate.sample_issued_line_tag
            << " owner_tag: " << gate.sample_issued_owner_tag
            << " owner_index: " << gate.sample_issued_owner_index
            << " owner_kind: " << static_cast<int>(gate.sample_issued_owner_kind)
            << " issue_meta: " << static_cast<int>(gate.sample_issued_issue_meta)
            << " family: " << static_cast<int>(gate.sample_issued_family)
            << " degree: " << static_cast<int>(gate.sample_issued_degree)
            << " page_max_degree_gt1: " << gate.sample_issued_page_max_degree_gt1
            << " issue_epoch: " << gate.sample_issued_epoch << std::endl;
}
