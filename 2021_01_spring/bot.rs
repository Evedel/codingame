mod bot {
  
}
use std::io;

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
  price : i32,
  path : Vec<String>,
  arena : Arena,
  state : State,
}

fn read_map() -> Map {
  let mut map = vec![];
  for _i in 0..37 {
    let is_tree = false;
    let is_mine = false;
    let is_dormant = false;
    let is_shadowed = false;
    let tree_size = -1;
    map.push(Cell{is_tree,is_mine,is_dormant,is_shadowed,tree_size})
  }
  let mut input_line = String::new();
  io::stdin().read_line(&mut input_line).unwrap();
  let number_of_trees = parse_input!(input_line, i32); // the current amount of trees
  for _i in 0..number_of_trees as usize {
    let mut input_line = String::new();
    io::stdin().read_line(&mut input_line).unwrap();
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

  map
}

fn read_actionlist() -> ActionList {
  let mut action_list = vec![];
  let mut input_line = String::new();
  io::stdin().read_line(&mut input_line).unwrap();
  let number_of_possible_actions = parse_input!(input_line, i32); // all legal actions
  for _i in 0..number_of_possible_actions as usize {
    let mut input_line = String::new();
    io::stdin().read_line(&mut input_line).unwrap();
    let possible_action = input_line.trim_matches('\n').to_string(); // try printing something from here to start with
    action_list.push(String::from(&possible_action));
  }
  action_list
}

fn read_game_state() -> State {
  let mut input_line = String::new();
  io::stdin().read_line(&mut input_line).unwrap();
  let day = parse_input!(input_line, i32); // the game lasts 24 days: 0-23
  let mut input_line = String::new();
  io::stdin().read_line(&mut input_line).unwrap();
  let nutrients = parse_input!(input_line, i32); // the base score you gain from the next COMPLETE action
  let mut input_line = String::new();
  io::stdin().read_line(&mut input_line).unwrap();
  let inputs = input_line.split(" ").collect::<Vec<_>>();
  let mut sun = vec![];
  let mut score = vec![];
  let mut is_waiting = vec![];
  sun.push(parse_input!(inputs[0], i32)); // your sun points
  score.push(parse_input!(inputs[1], i32));  // your current score
  is_waiting.push(false);
  let mut input_line = String::new();
  io::stdin().read_line(&mut input_line).unwrap();
  let inputs = input_line.split(" ").collect::<Vec<_>>();
  sun.push(parse_input!(inputs[0], i32)); // your sun points
  score.push(parse_input!(inputs[1], i32));  // your current score
  is_waiting.push(parse_input!(inputs[2], i32) == 1); // whether your opponent is asleep until the next day

  State{day, nutrients, sun, score, is_waiting}
}

fn read_arena() -> Arena {
  let mut arena = vec![];
  let mut input_line = String::new();
  io::stdin().read_line(&mut input_line).unwrap();
  let number_of_cells = parse_input!(input_line, i32); // 37
  for _i in 0..number_of_cells as usize {
    let mut input_line = String::new();
    let mut neighbors_ids = vec![];
    io::stdin().read_line(&mut input_line).unwrap();
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
      _ => {}
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

// def calculate_shadowed_trees(arena:List[Cell],day:int) -> List[Cell]:
//   direction_reversal = {0:3, 1:4, 2:5, 3:0, 4:1, 5:2}

//   shadow_to = day % 6
//   shadow_from = direction_reversal[shadow_to]
  
//   def cell_has_no_neighbour_at_direction(c: Cell, d:int) -> bool:
//     return (c.neigh_index[d] == -1)

//   shadow_casters: List[Cell] = []
//   for a in arena:
//     if cell_has_no_neighbour_at_direction(a,shadow_from):
//       shadow_casters.append(a)
  
//   while len(shadow_casters) > 0:
//     sc = shadow_casters.pop(0)
//     if sc.is_tree:
//       neigh_last = sc
//       for i in range(sc.tree_size):
//         neigh_index = neigh_last.neigh_index[shadow_to]
//         if neigh_index == -1:
//           break
//         else:
//           neigh = arena[neigh_index]
//           if neigh.is_tree and (neigh.tree_size <= sc.tree_size):
//             neigh.is_shadowed = True
//           neigh_last = neigh

//     neigh_index = sc.neigh_index[shadow_to]
//     if neigh_index != -1:
//       neigh = arena[neigh_index]
//       shadow_casters.append(neigh)

//   return arena

fn main() {
  let mut arena = read_arena();
  
  let mut visited = vec![];
  for _i in 0..37 {
    visited.push(false)
  }
  enumerate_hex_to_matrix(&mut arena, &mut visited, 0, 3, 6);
  loop {
    let state = read_game_state(); // Get input context
    let map = read_map(); // Get input forest
    let action_list = read_actionlist(); // List of possible actions

    print_map(&arena,&map);
    for s in &action_list {
      eprintln!("Action : {}", s);
    }

    match action_list.last() {
      None => println!("WAIT"),
      Some(action) => println!("{}", action)
    }
  }
}

#[cfg(test)]
mod tests {
  use super::*;

  fn get_starting_snapshot() -> Snapshot {
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

    let state = State{
      day:0,
      nutrients:20,
      sun:vec![2,2],
      score:vec![0,0],
      is_waiting:vec![false,false],
    };
    let snapshot = Snapshot{
      arena:arena,
      price:0,
      path:vec![],
      state:state,
    };
    

    snapshot
  }

  #[test]
  fn test_enumerate_hex_to_matrix() {
    let snap = get_starting_snapshot();
    assert_eq!(snap.arena[0].index_x, 3);
    assert_eq!(snap.arena[0].index_y, 6);

    assert_eq!(snap.arena[1].index_x, 3);
    assert_eq!(snap.arena[1].index_y, 8);

    assert_eq!(snap.arena[2].index_x, 2);
    assert_eq!(snap.arena[2].index_y, 7);

    assert_eq!(snap.arena[3].index_x, 2);
    assert_eq!(snap.arena[3].index_y, 5);

    assert_eq!(snap.arena[4].index_x, 3);
    assert_eq!(snap.arena[4].index_y, 4);

    assert_eq!(snap.arena[5].index_x, 4);
    assert_eq!(snap.arena[5].index_y, 5);

    assert_eq!(snap.arena[6].index_x, 4);
    assert_eq!(snap.arena[6].index_y, 7);
  }

  #[test]
  fn test_dist() {
    let snap = get_starting_snapshot();
    let s0 = &snap.arena[0];
    for s in &snap.arena {
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
}