package com.msarecom.user_interaction.service;

import com.msarecom.product.model.Product;
import com.msarecom.user_interaction.model.Interaction;
import com.msarecom.user_interaction.repository.InteractionRepository;
import org.apache.catalina.User;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Service;
import org.springframework.web.client.RestTemplate;

import java.util.List;

@Service
public class InteractionService {
    @Autowired
    private InteractionRepository interactionRepository;

    @Autowired
    private RestTemplate restTemplate;

    @Value("${user.service.url}")
    private String userServiceUrl;

    @Value("${product.service.url}")
    private String productServiceUrl;

    public List<Interaction> getAllInteractions() {
        return interactionRepository.findAll();
    }

    public Interaction getInteractionById(Long id) {
        return interactionRepository.findById(id).orElse(null);
    }

    public Interaction createInteraction(Interaction interaction) {
        // Validate user and product IDs
        if (validateUserId(interaction.getUserId()) && validateProductId(interaction.getProductId())) {
            return interactionRepository.save(interaction);
        }
        return null;
    }

    public void deleteInteraction(Long id) {
        interactionRepository.deleteById(id);
    }

    private boolean validateUserId(Long userId) {
        ResponseEntity<User> response = restTemplate.getForEntity(userServiceUrl + "/" + userId, User.class);
        return response.getStatusCode() == HttpStatus.OK;
    }

    private boolean validateProductId(Long productId) {
        ResponseEntity<Product> response = restTemplate.getForEntity(productServiceUrl + "/" + productId, Product.class);
        return response.getStatusCode() == HttpStatus.OK;
    }
}
