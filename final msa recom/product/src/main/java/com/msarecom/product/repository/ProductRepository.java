package com.msarecom.product.repository;

import com.msarecom.product.model.Product;
import org.springframework.data.jpa.repository.JpaRepository;


public interface ProductRepository extends JpaRepository<Product, Long> {
}

