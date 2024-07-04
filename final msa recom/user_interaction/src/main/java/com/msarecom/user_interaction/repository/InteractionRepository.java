package com.msarecom.user_interaction.repository;

import com.msarecom.user_interaction.model.Interaction;
import org.springframework.data.jpa.repository.JpaRepository;

public interface InteractionRepository extends JpaRepository<Interaction, Long> {
}

