package com.msarecom.user_interaction.controller;


import com.msarecom.user_interaction.model.Interaction;
import com.msarecom.user_interaction.repository.InteractionRepository;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.web.bind.annotation.*;

@RestController
@RequestMapping("/interactions")
@CrossOrigin(origins = "*")
public class InteractionController {

    @Autowired
    private InteractionRepository interactionRepository;

    @PostMapping
    public Interaction createInteraction(@RequestBody Interaction interaction) {
        return interactionRepository.save(interaction);
    }

    @GetMapping
    public Iterable<Interaction> getAllInteractions() {
        return interactionRepository.findAll();
    }
}
