/// Module CFR principal
pub mod engine;
pub mod trainer;
pub mod abstraction;

pub use engine::CfrEngine;
pub use trainer::CfrTrainer;
pub use abstraction::{CardAbstraction, AbstractionManager};