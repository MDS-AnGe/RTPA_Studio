/// Module CFR principal
pub mod engine;
pub mod trainer;
pub mod abstraction;
pub mod full_engine;

pub use engine::CfrEngine;
pub use trainer::CfrTrainer;
pub use abstraction::{CardAbstraction, AbstractionManager};
pub use full_engine::{FullCfrEngine, FullCfrTrainer};