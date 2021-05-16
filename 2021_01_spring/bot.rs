use std::io;
use std::time::{Duration, Instant};

macro_rules! parse_input {
  ($x:expr, $t:ident) => ($x.trim().parse::<$t>().unwrap())
}

struct Cell {
  is_tree : bool,
  is_mine : bool,
  is_dormant : bool,
  is_shadowed : bool,
  tree_size : i32,
}

type Map = Vec<Cell>;

type ActionList = Vec<String>;

struct State {
  day : i32,
  nutrients : i32,
  sun : Vec<i32>,
  score : Vec<i32>,
  is_waiting : Vec<bool>,
}

struct Hex {
  index_x : i32,
  index_y : i32,
  richness : i32,
  neighbors_ids : Vec<i32>,
}

type Arena = Vec<Hex>;

struct Snapshot {
  price : f32,
  path : Vec<String>,
  map : Map,
  state : State,
}

fn clone_map(map : &Map) -> Map {
  let mut map_new = vec![];
  for m in map {
    map_new.push(Cell{
      is_tree : m.is_tree,
      is_mine : m.is_mine,
      is_dormant : m.is_dormant,
      is_shadowed : m.is_shadowed,
      tree_size : m.tree_size,
    });
  }

  map_new
}

fn clone_state(state : &State) -> State {
  State{
    day: state.day,
    nutrients : state.nutrients,
    sun : state.sun.clone(),
    score : state.score.clone(),
    is_waiting : state.is_waiting.clone(),
  }
}

fn clone_snapshot(snap : &Snapshot) -> Snapshot {
  Snapshot{
    price : snap.price,
    path : snap.path.clone(),
    map : clone_map(&snap.map),
    state : clone_state(&snap.state),
  }
}

fn read_map(map : &mut Map) {
  let input_line = read_input_line();
  let number_of_trees = parse_input!(input_line, i32); // the current amount of trees
  for _i in 0..number_of_trees as usize {
    let input_line = read_input_line();
    let inputs = input_line.split(" ").collect::<Vec<_>>();
    let index = parse_input!(inputs[0], usize); // location of this tree
    let size = parse_input!(inputs[1], i32); // size of this tree: 0-3
    let is_mine = parse_input!(inputs[2], i32) == 1; // 1 if this is your tree
    let is_dormant = parse_input!(inputs[3], i32) == 1; // 1 if this tree is dormant
    map[index].is_tree = true;
    map[index].is_mine = is_mine;
    map[index].is_dormant = is_dormant;
    map[index].is_shadowed = false;
    map[index].tree_size = size;
  }
}

fn read_actionlist() -> ActionList {
  let mut action_list = vec![];
  let input_line = read_input_line();
  let number_of_possible_actions = parse_input!(input_line, i32); // all legal actions
  for _i in 0..number_of_possible_actions as usize {
    let input_line = read_input_line();
    let possible_action = input_line.trim_matches('\n').to_string(); // try printing something from here to start with
    action_list.push(String::from(&possible_action));
  }
  action_list
}

fn read_game_state(state: &mut State) {
  let input_line = read_input_line();
  state.day = parse_input!(input_line, i32); // the game lasts 24 days: 0-23
  let input_line = read_input_line();
  state.nutrients = parse_input!(input_line, i32); // the base score you gain from the next COMPLETE action
  let input_line = read_input_line();
  let inputs = input_line.split(" ").collect::<Vec<_>>();
  // let mut sun = vec![];
  // let mut score = vec![];
  // let mut is_waiting = vec![];
  state.sun[1] = parse_input!(inputs[0], i32);
  state.score[1] = parse_input!(inputs[1], i32);
  state.is_waiting[1] = false;
  let input_line = read_input_line();
  let inputs = input_line.split(" ").collect::<Vec<_>>();
  state.sun[0] = parse_input!(inputs[0], i32);
  state.score[0] = parse_input!(inputs[1], i32);
  state.is_waiting[0] = parse_input!(inputs[2], i32) == 1;
}

fn read_arena() -> Arena {
  let mut arena = vec![];
  let input_line = read_input_line();
  let number_of_cells = parse_input!(input_line, i32); // 37
  for _i in 0..number_of_cells as usize {
    let mut neighbors_ids = vec![];
    let input_line = read_input_line();
    let inputs = input_line.split(" ").collect::<Vec<_>>();
    let _index = parse_input!(inputs[0], i32); // 0 is the center cell, the next cells spiral outwards
    let richness = parse_input!(inputs[1], i32); // 0 if the cell is unusable, 1-3 for usable cells
    for j in 2..8 {
      neighbors_ids.push(parse_input!(inputs[j], i32));
    }
    arena.push(Hex{richness, neighbors_ids, index_x:-1, index_y:-1})
  }

  arena
}

fn read_input_line() -> String {
  let mut input_line = String::new();
  io::stdin().read_line(&mut input_line).unwrap();
  // eprintln!("{}", input_line);
  input_line
}

fn enumerate_hex_to_matrix(
  arena : &mut Arena, visited : &mut Vec<bool>,
  index : usize, index_x : i32, index_y : i32
) {
  arena[index].index_x = index_x;
  arena[index].index_y = index_y;
  visited[index] = true;
  for i in 0..6 {
    if arena[index].neighbors_ids[i] == -1 {
      continue
    }

    let neib_index = *&arena[index].neighbors_ids[i] as usize;
    if visited[neib_index] {
      continue
    }

    let mut next_index_x = index_x;
    let mut next_index_y = index_y;

    match i {
      0 => { next_index_y += 2; }
      1 => { next_index_x -= 1; next_index_y += 1; }
      2 => { next_index_x -= 1; next_index_y -= 1; }
      3 => { next_index_y -= 2; }
      4 => { next_index_x += 1; next_index_y -= 1; }
      5 => { next_index_x += 1; next_index_y += 1; }
      _ => { panic!("> _ < "); },
    }
    enumerate_hex_to_matrix(arena, visited, neib_index, next_index_x, next_index_y)
  }
}

fn print_map(arena : &Arena, map : &Map) {
  let mut line = vec![];
  for _i in 0..13*7 {
    line.push(String::from("."));
  }
  let trees_shadow = vec!['f','t','F','T'];
  let trees_opened = vec!['n','m','N','M'];
  for i in 0..37 {
    let dx = arena[i].index_x;
    let dy = arena[i].index_y;
    let str_val = arena[i].richness.to_string();
    let il = (dx*13 + dy) as usize;
    line[il] = str_val;
    if map[i].is_tree {
      if map[i].is_shadowed {
        line[il] = trees_shadow[map[i].tree_size as usize].to_string();
      } else {
        line[il] = trees_opened[map[i].tree_size as usize].to_string();
      }
    }
  }

  let mut print_line = String::from("");
  for i in 0..7 {
    for c in &line[13*i..13*(i+1)] {
      print_line += c;
    }
    print_line += "\n";
  }
  eprintln!("{}",print_line);
}

fn dist(h1 : &Hex, h2 : &Hex) -> i32 {
  let dy = h1.index_y - h2.index_y;
  let dx = h1.index_x - h2.index_x;
  if dy.abs() < 2 { return dx.abs() }
  return (dx.abs() + dy.abs())/2
}

fn cell_has_no_neighbour_at_direction(h1 : &Hex, dir : &i32) -> bool {
  return h1.neighbors_ids[*dir as usize] == -1
}

fn calculate_shadowed_trees(arena : &Arena, map : &mut Map, day : i32) {
  let direction_reversal = vec![3, 4, 5, 0, 1, 2];
  let shadow_to = (day % 6) as usize;
  let shadow_from = direction_reversal[shadow_to];
  let mut shadow_casters = vec![];

  for i in 0..arena.len() {
    if cell_has_no_neighbour_at_direction(&arena[i], &shadow_from) {
      shadow_casters.push(i);
    }
  }
  loop {
    let sc = shadow_casters.pop();
    match sc {
      None => break,
      Some(initial_hex_id) => {
        if map[initial_hex_id].is_tree {
          let mut next_hex_id = &arena[initial_hex_id].neighbors_ids[shadow_to];
          for _i2 in 0..map[initial_hex_id].tree_size {
            if *next_hex_id == -1 {
              break;
            }
            let next_hex_id_usize = *next_hex_id as usize;
            if map[next_hex_id_usize].is_tree &&
              (map[next_hex_id_usize].tree_size <= map[initial_hex_id].tree_size)
            {
              map[next_hex_id_usize].is_shadowed = true;
            }
            next_hex_id = &arena[next_hex_id_usize].neighbors_ids[shadow_to];
          }
        }
        
        let next_hex_id = &arena[initial_hex_id].neighbors_ids[shadow_to];
        if *next_hex_id != -1 {
          shadow_casters.push(*next_hex_id as usize);
        }
      }
    }
  }
}

fn clear_shadows(snap : &mut Snapshot) {
  for i in 0..snap.map.len() {
    snap.map[i].is_shadowed = false;
  }
}

fn calculate_price(arena : &Arena, snap : &mut Snapshot) {
  let whoami = true;
  let myid = whoami as usize;
  let mut price = 0.0;
  let max_days = 24.0;
  let day_muliplier = (max_days - snap.state.day as f32)/max_days;
  // let mut new_suns = 0;

  let mut day_switch = 1.0;
  if snap.state.day < 20 {
    day_switch = 0.1;
  }
  for i in 0..arena.len() {
    if snap.map[i].is_tree && 
        snap.map[i].is_mine &&
        !snap.map[i].is_shadowed
    {
      let tree_size_price = (snap.map[i].tree_size*snap.map[i].tree_size) as f32 + 1.0*day_switch;
      price += tree_size_price*arena[i].richness as f32 * day_muliplier;
      // new_suns += snap.map[i].tree_size;
    }
  }

  price += snap.state.score[myid] as f32 * day_switch;
  // price += new_suns as f32 * day_muliplier * (1.0 - day_switch);
  // price += snap.state.sun[myid] as f32 * day_muliplier;
  snap.price = price;
}

fn get_trees_numbers(snap : &Snapshot) -> Vec<i32> {
  let mut tree_nubers = vec![0,0,0,0];

  for i in 0..snap.map.len() {
    if snap.map[i].is_tree && snap.map[i].is_mine {
      tree_nubers[snap.map[i].tree_size as usize] += 1;
    }
  }

  return tree_nubers;
}

fn get_all_seed_actions(actions : &mut Vec<String>, snap : &Snapshot, arena : &Arena, cell_id : usize) {
  for i in 0..snap.map.len() {
    if !snap.map[i].is_tree &&
      (arena[i].richness > 0) &&
      (dist(&arena[cell_id],&arena[i]) <= snap.map[cell_id].tree_size)
    {
      actions.push(format!("SEED {} {}",cell_id, i));
    }
  }
}

fn get_all_actions(snap : &Snapshot, arena: &Arena) -> Vec<String> {
  let tree_fix_cost = vec![0,1,3,7];
  let tree_add_cost = get_trees_numbers(snap);
  let mut actions = vec![];
  actions.push(String::from("WAIT"));
  for i in 0..arena.len() {
    if snap.map[i].is_tree &&
      snap.map[i].is_mine &&
      !snap.map[i].is_dormant
    {
      if (snap.map[i].tree_size != 0) && 
        (tree_fix_cost[0] + tree_add_cost[0] <= snap.state.sun[1])
      {
        get_all_seed_actions(&mut actions, snap, arena, i);
      }
      let tree_size = snap.map[i].tree_size as usize;
      if tree_size == 3 {
        actions.push(format!("COMPLETE {}", i));
      } else if tree_fix_cost[tree_size+1] + tree_add_cost[tree_size+1] <= snap.state.sun[1] {
        actions.push(format!("GROW {}", i));
      }
    }
  }

  actions
}

fn clear_map(map : &mut Map) {
  for i in 0..map.len() {
    map[i].is_dormant = false;
    map[i].is_mine = false;
    map[i].is_shadowed = false;
    map[i].is_tree = false;
    map[i].tree_size = -1;
  }
}

fn apply_wait(arena : &Arena, snap : &mut Snapshot) {
  if snap.state.day == 23 {
    let path_len = snap.path.len();
    if path_len > 2 {
      if snap.path[path_len-1] == "WAIT" && snap.path[path_len-2] == "WAIT" {
        snap.path.pop();
      }
    }
    return
  }

  let whoami = true;
  let myid = whoami as usize;

  snap.state.day += 1;
  for i in 0..snap.map.len() {
    if snap.map[i].is_tree {
      snap.map[i].is_dormant = false;
      snap.map[i].is_shadowed = false;  
    }
  }
  calculate_shadowed_trees(arena, &mut snap.map, snap.state.day);
  for i in 0..snap.map.len() {
    if snap.map[i].is_tree &&
      (whoami == snap.map[i].is_mine) &&
      (! snap.map[i].is_shadowed)
    {
      snap.state.sun[myid] += snap.map[i].tree_size;
    }
  }
}

fn apply_grow(snap : &mut Snapshot, index : usize) {
  let whoami = true;
  let myid = whoami as usize;
  let tree_fix_cost = vec![0,1,3,7];
  let tree_add_cost = get_trees_numbers(snap);
  snap.map[index].is_dormant = true;
  snap.map[index].tree_size += 1;
  let new_size = snap.map[index].tree_size as usize;
  snap.state.sun[myid] -= tree_fix_cost[new_size] + tree_add_cost[new_size];
}

fn apply_complete(arena : &Arena, snap : &mut Snapshot, index : usize) {
  let whoami = true;
  let myid = whoami as usize;
  let richness_bonus = vec![0,0,2,4];
  let richness = arena[index].richness as usize;
  snap.state.score[myid] += snap.state.nutrients + richness_bonus[richness];
  snap.state.nutrients -= 1;
  if snap.state.nutrients < 0 { snap.state.nutrients = 0 }
  snap.map[index].is_tree     = false;
  snap.map[index].is_dormant  = false;
  snap.map[index].is_mine     = false;
  snap.map[index].is_shadowed = false;
  snap.map[index].tree_size   = -1;
}

fn apply_seed(snap : &mut Snapshot, index_parent : usize, index_kid : usize) {
  let whoami = true;
  let myid = whoami as usize;
  let tree_add_cost = get_trees_numbers(snap);
  snap.map[index_parent].is_dormant = true;
  snap.map[index_kid].is_dormant = true;
  snap.map[index_kid].is_tree = true;
  snap.map[index_kid].is_mine = whoami;
  snap.map[index_kid].tree_size = 0;
  snap.state.sun[myid] -= tree_add_cost[0];
}

fn apply_step(snap : &Snapshot, arena : &Arena, action : String) -> Snapshot {
  let mut new_snapshot = clone_snapshot(snap);
  new_snapshot.path.push(action.to_string());
  let action_parts = action.split(" ").collect::<Vec<_>>();
  match action_parts[0] {
      "GROW" => apply_grow(&mut new_snapshot, parse_input!(action_parts[1], usize)),
      "SEED" => apply_seed(&mut new_snapshot, parse_input!(action_parts[1], usize),parse_input!(action_parts[2], usize)),
      "COMPLETE" => apply_complete(arena, &mut new_snapshot, parse_input!(action_parts[1], usize)),
      "WAIT" => apply_wait(arena, &mut new_snapshot),
      _ => { panic!("> _ <"); },
  }
  clear_shadows(&mut new_snapshot);
  calculate_shadowed_trees(arena, &mut new_snapshot.map, new_snapshot.state.day+1);
  calculate_price(arena, &mut new_snapshot);

  new_snapshot
}

fn get_next_snapshots(snapshots_now : &mut Vec<Snapshot>, snapshots_next : &mut Vec<Snapshot>, arena : &Arena) {
  loop {
    let snap_option = snapshots_now.pop();
    match snap_option {
      None => break,
      Some(snap) => {
        let actions = get_all_actions(&snap, arena);
        for a in actions {
          let snap_new = apply_step(&snap, arena, a);
          if snapshots_next.len() == 0 {
            snapshots_next.push(snap_new);
          } else {
            let aim_price = snap_new.price;
            let mut aim_index = 0 as usize;
            let mut found = false;
            for i in 0..snapshots_next.len() {
              if snapshots_next[i].price < aim_price {
                aim_index = i;
                found = true;
                break;
              }
            }
            if found {
              snapshots_next.insert(aim_index, snap_new);
            } else {
              snapshots_next.push(snap_new);
            }
          }
        }
      }
    }
  }
}

fn choose_best_snapshots(
  snapshots_now : &mut Vec<Snapshot>,
  snapshots_next: &mut Vec<Snapshot>,
  amount: &mut i32)
{
  let mut iter_limit = *amount as usize;
  let next_len = snapshots_next.len();
  if next_len < iter_limit {
    iter_limit = next_len;
  }
  let mut print_limit = 5;
  if iter_limit < print_limit {
    print_limit = iter_limit;
  }
  for j in 0..print_limit {
    eprintln!("{} {:?}", snapshots_next[j].price, snapshots_next[j].path);
  }
  for i in 0..iter_limit {
    snapshots_now.push(clone_snapshot(&snapshots_next[i]));
  }
  snapshots_next.clear();
}

fn get_next_step(snap : &mut Snapshot, arena : &Arena, layer_size : &mut i32) -> String {
  let start = Instant::now();

  let mut snap_now = vec![];
  let mut snap_next = vec![];

  calculate_shadowed_trees(&arena, &mut snap.map, snap.state.day+1);
  calculate_price(arena, snap);

  snap_now.push(clone_snapshot(snap));
  let mut i = 0;
  let mut duration;
  loop {
    i += 1;
    get_next_snapshots(&mut snap_now, &mut snap_next, arena);
    choose_best_snapshots(&mut snap_now, &mut snap_next, layer_size);
    duration = start.elapsed();
    if duration.as_millis() > 75 {
      break;
    }
  }
  if i > 100 {
    *layer_size += 5;
  }
  eprintln!("{} {} {:?}", i, layer_size, &duration);
  
  return snap_now[0].path[0].to_string()
}

fn main() {
  let mut arena = read_arena();
  
  let mut map = vec![];
  let mut visited = vec![];
  for _i in 0..arena.len() {
    visited.push(false);

    let is_tree = false;
    let is_mine = false;
    let is_dormant = false;
    let is_shadowed = false;
    let tree_size = -1;
    map.push(Cell{is_tree,is_mine,is_dormant,is_shadowed,tree_size})
  }
  
  let state = State{day:0,nutrients:0,is_waiting:vec![false,false],score:vec![0,0],sun:vec![0,0]};
  let mut snap = Snapshot{map:map, state:state,price:0.0,path:vec![]};
  enumerate_hex_to_matrix(&mut arena, &mut visited, 0, 3, 6);
  let mut layer_size = 20;
  loop {
    clear_map(&mut snap.map);
    read_game_state(&mut snap.state);
    read_map(&mut snap.map);
    read_actionlist();

    // print_map(&arena,&snap.map);
    let action = get_next_step(&mut snap, &arena, &mut layer_size);
    println!("{}", action);
  }
}

// 
// 
//  PLEASE DONT READ
// 
//     TESTS ONLY
// 
// 

#[cfg(test)]
mod tests {
  use super::*;

  fn get_starting_snapshot() -> (Snapshot, Arena) {
    let mut arena = vec![];
    arena.push(Hex{index_x: -1,index_y: -1,richness: 3,
      neighbors_ids: vec![1,2,3,4,5,6],
    }); // 0
    arena.push(Hex{index_x: -1,index_y: -1,richness: 3,
      neighbors_ids: vec![7,8,2,0,6,18],
    }); // 1
    arena.push(Hex{index_x: -1,index_y: -1,richness: 3,
      neighbors_ids: vec![8,9,10,3,0,1],
    }); // 2
    arena.push(Hex{index_x: -1,index_y: -1,richness: 3,
      neighbors_ids: vec![2,10,11,12,4,0],
    }); // 3
    arena.push(Hex{index_x: -1,index_y: -1,richness: 3,
      neighbors_ids: vec![0,3,12,13,14,5],
    }); // 4
    arena.push(Hex{index_x: -1,index_y: -1,richness: 3,
      neighbors_ids: vec![6,0,4,14,15,16],
    }); // 5
    arena.push(Hex{index_x: -1,index_y: -1,richness: 3,
      neighbors_ids: vec![18,1,0,5,16,17],
    }); // 6
    arena.push(Hex{index_x: -1,index_y: -1,richness: 2,
      neighbors_ids: vec![-1,-1,8,1,18,-1],
    }); // 7
    arena.push(Hex{index_x: -1,index_y: -1,richness: 2,
      neighbors_ids: vec![-1,-1,9,2,1,7],
    }); // 8
    arena.push(Hex{index_x: -1,index_y: -1,richness: 2,
      neighbors_ids: vec![-1,-1,-1,10,2,8],
    }); // 9
    arena.push(Hex{index_x: -1,index_y: -1,richness: 2,
      neighbors_ids: vec![9,-1,-1,11,3,2],
    }); // 10
    arena.push(Hex{index_x: -1,index_y: -1,richness: 2,
      neighbors_ids: vec![10,-1,-1,-1,12,3],
    }); // 11
    arena.push(Hex{index_x: -1,index_y: -1,richness: 2,
      neighbors_ids: vec![3,11,-1,-1,13,4],
    }); // 12
    arena.push(Hex{index_x: -1,index_y: -1,richness: 2,
      neighbors_ids: vec![4,12,-1,-1,-1,14],
    }); // 13
    arena.push(Hex{index_x: -1,index_y: -1,richness: 2,
      neighbors_ids: vec![5,4,13,-1,-1,15],
    }); // 14
    arena.push(Hex{index_x: -1,index_y: -1,richness: 2,
      neighbors_ids: vec![16,5,14,-1,-1,-1],
    }); // 15
    arena.push(Hex{index_x: -1,index_y: -1,richness: 2,
      neighbors_ids: vec![17,6,5,15,-1,-1],
    }); // 16
    arena.push(Hex{index_x: -1,index_y: -1,richness: 2,
      neighbors_ids: vec![-1,18,6,16,-1,-1],
    }); // 17
    arena.push(Hex{index_x: -1,index_y: -1,richness: 2,
      neighbors_ids: vec![-1,7,1,6,17,-1],
    }); // 18

    let mut visited = vec![];
    for _i in 0..37 {
      visited.push(false)
    }
    enumerate_hex_to_matrix(&mut arena, &mut visited, 0, 3, 6);

    let mut map = vec![];
    for _i in 0..arena.len() {
      map.push(Cell{
        is_tree: false,
        is_dormant: false,
        is_mine: false,
        is_shadowed: false,
        tree_size: -1,
      })
    }

    let state = State{
      day:0,
      nutrients:20,
      sun:vec![2,2],
      score:vec![0,0],
      is_waiting:vec![false,false],
    };
    let snapshot = Snapshot{
      price:0.0,
      path:vec![],
      state:state,
      map: map,
    };
    

    (snapshot, arena)
  }
  #[test]
  fn test_enumerate_hex_to_matrix() {
    let (_snap, arena) = get_starting_snapshot();
    assert_eq!(arena[0].index_x, 3);
    assert_eq!(arena[0].index_y, 6);

    assert_eq!(arena[1].index_x, 3);
    assert_eq!(arena[1].index_y, 8);

    assert_eq!(arena[2].index_x, 2);
    assert_eq!(arena[2].index_y, 7);

    assert_eq!(arena[3].index_x, 2);
    assert_eq!(arena[3].index_y, 5);

    assert_eq!(arena[4].index_x, 3);
    assert_eq!(arena[4].index_y, 4);

    assert_eq!(arena[5].index_x, 4);
    assert_eq!(arena[5].index_y, 5);

    assert_eq!(arena[6].index_x, 4);
    assert_eq!(arena[6].index_y, 7);
  }
  #[test]
  fn test_dist() {
    let (_snap, arena) = get_starting_snapshot();
    let s0 = &arena[0];
    for s in &arena {
      if (s.index_x == s0.index_x) && (s.index_y == s0.index_y) {
        assert_eq!(dist(s, s0), 0);
      } else {
        if s.richness == 3 {
          assert_eq!(dist(s, s0), 1);
        }
        if s.richness == 2 {
          assert_eq!(dist(s, s0), 2);
        }
      }
    }
  }
  #[test]
  fn test_shadow_calc() {
    let (mut snap, arena) = get_starting_snapshot();
    let mut day = 0;
    snap.map[0].is_tree = true;
    snap.map[0].tree_size = 0;
    snap.map[1].is_tree = true;
    snap.map[1].tree_size = 0;
    calculate_shadowed_trees(&arena, &mut snap.map, day);
    assert_eq!(snap.map[1].is_shadowed, false);

    clear_shadows(&mut snap);
    snap.map[1].tree_size = 1;
    calculate_shadowed_trees(&arena, &mut snap.map, day);
    assert_eq!(snap.map[1].is_shadowed, false);

    clear_shadows(&mut snap);
    snap.map[0].tree_size = 1;
    calculate_shadowed_trees(&arena, &mut snap.map, day);
    assert_eq!(snap.map[1].is_shadowed, true);

    clear_shadows(&mut snap);
    snap.map[1].is_tree = false;
    snap.map[7].is_tree = true;
    snap.map[7].tree_size = 1;
    calculate_shadowed_trees(&arena, &mut snap.map, day);
    assert_eq!(snap.map[7].is_shadowed, false);

    clear_shadows(&mut snap);
    snap.map[0].tree_size = 2;
    calculate_shadowed_trees(&arena, &mut snap.map, day);
    assert_eq!(snap.map[7].is_shadowed, true);

    clear_shadows(&mut snap);
    day = 1;
    snap.map[9].is_tree = true;
    snap.map[9].tree_size = 1;
    snap.map[2].is_tree = true;
    snap.map[2].tree_size = 3;
    calculate_shadowed_trees(&arena, &mut snap.map, day);
    assert_eq!(snap.map[7].is_shadowed, false);
    assert_eq!(snap.map[9].is_shadowed, true);
    assert_eq!(snap.map[2].is_shadowed, false);
  }
  #[test]
  fn test_get_all_actions() {
    let (mut snap, arena) = get_starting_snapshot();
    let actions = get_all_actions(&snap, &arena);
    assert_eq!(actions.len(), 1);
    assert_eq!(actions[0], String::from("WAIT"));

    snap.map[0].is_tree = true;
    snap.map[0].is_mine = true;
    snap.map[0].tree_size = 0;
    let actions = get_all_actions(&snap, &arena);
    assert_eq!(actions.len(), 2);
    assert_eq!(actions[0], String::from("WAIT"));
    assert_eq!(actions[1], String::from("GROW 0"));

    snap.map[0].is_tree = true;
    snap.map[0].is_mine = true;
    snap.map[0].tree_size = 1;
    let actions = get_all_actions(&snap, &arena);
    assert_eq!(actions.len(), 7);
    assert_eq!(actions[0], String::from("WAIT"));
    for i in 1..7 {
      assert_eq!(actions[i], format!("SEED {} {}",0,i));
    }

    snap.state.sun[1] = 3;
    let actions = get_all_actions(&snap, &arena);
    assert_eq!(actions.len(), 8);
    assert_eq!(actions[0], String::from("WAIT"));
    for i in 1..7 {
      assert_eq!(actions[i], format!("SEED {} {}",0,i));
    }
    assert_eq!(actions[7], String::from("GROW 0"));

    snap.state.sun[1] = 7;
    snap.map[0].tree_size = 2;
    let actions = get_all_actions(&snap, &arena);
    assert_eq!(actions.len(), 20);
    assert_eq!(actions[0], String::from("WAIT"));
    for i in 1..19 {
      assert_eq!(actions[i], format!("SEED {} {}",0,i));
    }
    assert_eq!(actions[19], String::from("GROW 0"));

    snap.state.sun[1] = 4;
    snap.map[0].tree_size = 3;
    let actions = get_all_actions(&snap, &arena);
    assert_eq!(actions.len(), 20);
    assert_eq!(actions[0], String::from("WAIT"));
    for i in 1..19 {
      assert_eq!(actions[i], format!("SEED {} {}",0,i));
    }
    assert_eq!(actions[19], String::from("COMPLETE 0"));
  }
}