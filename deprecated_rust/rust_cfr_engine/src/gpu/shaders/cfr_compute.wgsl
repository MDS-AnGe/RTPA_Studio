// CFR Compute Shader pour GPU
// Calculs CFR parallèles ultra-rapides

struct StateData {
    hole_cards: vec2f,     // rank, suit pour 2 cartes
    community: array<vec2f, 5>, // 5 cartes communautaires max
    pot_size: f32,
    stack_size: f32,
    position: f32,
    num_players: f32,
    betting_round: f32,    // 0=preflop, 1=flop, 2=turn, 3=river
    actions_mask: f32,     // Bitmask des actions disponibles
    padding: array<f32, 240>, // Padding pour 256 floats total
}

struct ResultData {
    convergence: f32,
    node_value: f32,
    regret_sum: f32,
    strategy_sum: f32,
    padding: array<f32, 252>, // Total 256 floats
}

@group(0) @binding(0) var<storage, read> input_data: array<StateData>;
@group(0) @binding(1) var<storage, read_write> output_data: array<ResultData>;

// Fonction d'évaluation de main simplifiée
fn evaluate_hand_strength(hole_cards: vec2f, community: array<vec2f, 5>, num_community: u32) -> f32 {
    var strength = 0.0;
    
    // Évaluation basique basée sur la hauteur de carte
    strength += hole_cards.x * 0.1;  // Première carte
    strength += hole_cards.y * 0.05; // Deuxième carte (suit moins important)
    
    // Bonus pour cartes communautaires
    for (var i = 0u; i < num_community; i = i + 1u) {
        strength += community[i].x * 0.02;
        
        // Bonus paire avec hole cards
        if (community[i].x == hole_cards.x) {
            strength += 2.0;
        }
    }
    
    return clamp(strength, 0.0, 10.0);
}

// Calcul de probabilité d'action basée sur regret matching
fn compute_action_probability(regret: f32, total_regret: f32) -> f32 {
    if (total_regret > 0.0) {
        return max(regret, 0.0) / total_regret;
    } else {
        return 0.25; // Stratégie uniforme si pas de regrets positifs
    }
}

// Fonction de hash simple pour information set
fn hash_info_set(hole_cards: vec2f, community: array<vec2f, 5>, betting_round: f32, position: f32) -> u32 {
    var hash_val = 0u;
    hash_val = hash_val * 31u + u32(hole_cards.x);
    hash_val = hash_val * 31u + u32(hole_cards.y);
    hash_val = hash_val * 31u + u32(betting_round);
    hash_val = hash_val * 31u + u32(position);
    
    // Ajouter cartes communautaires selon betting round
    let num_community = u32(betting_round) + 3u;
    for (var i = 0u; i < min(num_community, 5u); i = i + 1u) {
        hash_val = hash_val * 31u + u32(community[i].x);
    }
    
    return hash_val;
}

// Thread principal compute
@compute @workgroup_size(64, 1, 1)
fn main(@builtin(global_invocation_id) global_id: vec3<u32>) {
    let index = global_id.x;
    
    // Vérifier limites
    if (index >= arrayLength(&input_data)) {
        return;
    }
    
    let state = input_data[index];
    var result = ResultData();
    
    // Identifier le nombre de cartes communautaires selon betting round
    let num_community = u32(state.betting_round) * 3u + 3u; // 3 flop, 4 turn, 5 river
    let clamped_community = min(num_community, 5u);
    
    // Évaluer force de la main
    let hand_strength = evaluate_hand_strength(state.hole_cards, state.community, clamped_community);
    
    // Calculer hash information set
    let info_hash = hash_info_set(state.hole_cards, state.community, state.betting_round, state.position);
    
    // Actions disponibles (décodage du bitmask)
    let has_fold = (u32(state.actions_mask) & 1u) != 0u;
    let has_call = (u32(state.actions_mask) & 2u) != 0u;
    let has_check = (u32(state.actions_mask) & 4u) != 0u;
    let has_bet = (u32(state.actions_mask) & 8u) != 0u;
    let has_raise = (u32(state.actions_mask) & 16u) != 0u;
    let has_allin = (u32(state.actions_mask) & 32u) != 0u;
    
    // Compter nombre d'actions
    var num_actions = 0u;
    if (has_fold) { num_actions = num_actions + 1u; }
    if (has_call) { num_actions = num_actions + 1u; }
    if (has_check) { num_actions = num_actions + 1u; }
    if (has_bet) { num_actions = num_actions + 1u; }
    if (has_raise) { num_actions = num_actions + 1u; }
    if (has_allin) { num_actions = num_actions + 1u; }
    
    // Calcul CFR simplifié pour GPU
    var total_regret = 0.0;
    var fold_regret = 0.0;
    var call_regret = 0.0;
    var bet_regret = 0.0;
    
    // Simulation Monte Carlo rapide
    let pot_odds = state.pot_size / (state.pot_size + state.stack_size * 0.5);
    let win_probability = (hand_strength + f32(info_hash % 100u) * 0.01) * 0.1;
    
    // Calculer regrets basés sur force de main et pot odds
    if (has_fold) {
        fold_regret = -(state.pot_size * 0.1); // Coût d'opportunité
        total_regret += max(fold_regret, 0.0);
    }
    
    if (has_call) {
        call_regret = (win_probability - pot_odds) * state.pot_size;
        total_regret += max(call_regret, 0.0);
    }
    
    if (has_bet || has_raise) {
        bet_regret = (win_probability - 0.6) * state.pot_size * 1.5;
        total_regret += max(bet_regret, 0.0);
    }
    
    // Calculer stratégie actuelle
    let fold_prob = compute_action_probability(fold_regret, total_regret);
    let call_prob = compute_action_probability(call_regret, total_regret);
    let bet_prob = compute_action_probability(bet_regret, total_regret);
    
    // Node value estimation
    var node_value = 0.0;
    if (has_fold) { node_value += fold_prob * fold_regret; }
    if (has_call) { node_value += call_prob * call_regret; }
    if (has_bet || has_raise) { node_value += bet_prob * bet_regret; }
    
    // Metric de convergence (variance des regrets)
    let regret_variance = (fold_regret - node_value) * (fold_regret - node_value) +
                         (call_regret - node_value) * (call_regret - node_value) +
                         (bet_regret - node_value) * (bet_regret - node_value);
    
    // Remplir résultats
    result.convergence = sqrt(regret_variance / f32(max(num_actions, 1u)));
    result.node_value = node_value;
    result.regret_sum = total_regret;
    result.strategy_sum = fold_prob + call_prob + bet_prob;
    
    // Écrire résultats
    output_data[index] = result;
}